# encoding: utf8
################################################################################
# 描述：实现前处理相关功能
# 1、根据几何参数生成实体并划分单元
# 2、读入单元及节点信息
# 日期：2014-12-22
################################################################################

import os
import numpy as np

def generate_mesh(filename,radius,length,size="0.2"):
	'''
	* 功能：根据参数创建几何体并划分网格
	* 输入：保存的文件名，坯料半径，坯料长度，网格尺寸因子(0,1]
	* 输出：网格划分结果
	'''
	# 创建几何体的gmsh代码
	# 参见http://www.geuz.org/gmsh/doc/texinfo/gmsh.html#Post_002dprocessing-options-list
	code = '''lc = #lc#;
		R = #radius#;
		L = #length#;
		Point(1) = {0, 0, 0, lc};
		Point(2) = {0, R, 0, lc};
		Line(1) = {1,2};
		ex[] = Extrude {L,0,0} { Line{1}; Layers{{L/lc}, {1}};};
		Physical Volume(1) = ex[1];'''
	### 修改网格尺寸并保存为gmsh输入文件
	code = code.replace('#radius#', str(radius)).replace('#length#', str(length)).replace('#lc#', str(size))
	geofile = "%s.geo" % filename
	f = open(geofile, "w")
	try:
		f.write(code)
	finally:
		f.close()
	### 命令行执行网格划分程序
	fail = os.system("gmsh %s -2" % geofile) # gmsh网格划分
	succ = not fail
	return succ

def read_elements(filename,element_type):
	'''
	* 功能：读取网格文件到单元数组及节点数组
	* 输入：网格文件名，单元类型
	* 输出：单元数组，节点坐标数组
	'''
	### gmsh文件格式：
	# $Nodes
	# number_of_nodes
	# node_id x y z
	# ...
	# $EndNodes
	# $Elements
	# number_of elements
	# element_id element_type number_of_tags physical elementary nodes_list
	# $EndElements
	# 单元类型：
	# 1	Line	(2 nodes, 1 edge).
	# 2	Triangle	(3 nodes, 3 edges).
	# 3	Quadrangle	(4 nodes, 4 edges).
	# 4	Tetrahedron	(4 nodes, 6 edges, 4 facets).
	# 5	Hexahedron	(8 nodes, 12 edges, 6 facets).
	# 6	Prism	(6 nodes, 9 edges, 5 facets).
	# 7	Pyramid	(5 nodes, 8 edges, 5 facets).
	# 15	Point	(1 node).
	### 读取行
	mshfile = "%s.msh" % filename
	f = open(mshfile)
	try:
		lines = f.readlines()
	finally:
		f.close()
	lines = [x.strip('\n') for x in lines] # 去掉换行符
	### 文件标记
	FLAG_NODE = "$Nodes"
	FLAG_ELEMENT = "$Elements"
	nde_bgn = lines.index(FLAG_NODE) + 1
	ele_bgn = lines.index(FLAG_ELEMENT) + 1

	### 节点数，单元数
	num_nde = int(lines[nde_bgn])
	num_ele = int(lines[ele_bgn]) # 可能还包括了不需要的单元类型，所以后面需要修正

	### 节点数组
	node_list = [] 
	for node_line in lines[nde_bgn+1:nde_bgn+num_nde+1]:
		node_temp = [float(x) for x in node_line.split()[1:]]
		node_list.append(node_temp)
	NODES = np.array(node_list)

	### 单元数组
	element_list = [] 
	for element_line in lines[ele_bgn+1:ele_bgn+num_ele+1]:
		element_line_list = element_line.split()

		# 针对正确类型单元
		if int(element_line_list[1]) == element_type :
			# 注意：gmsh中节点编号从1开始，而numpy数组index从0开始，所以减1
			element_temp = [int(x)-1 for x in element_line_list[5:]] 
			element_list.append(element_temp)

	ELEMENTS = np.array(element_list)
	return ELEMENTS,NODES

def belongs_to_element(elements,node_list):
	'''
	* 功能：根据节点号找出隶属的单元集合（包含任一目标节点的单元都将被统计）
	* 输入：所有单元、节点号集合
	* 输出：隶属的单元号集合
	'''
	node_list.shape = -1,1
	t = np.array([x in node_list for x in elements])
	index = np.arange(0,len(elements))
	return index[t]

def save_data(filename,postname, data, order=1, timestep=1):
	'''
	* 功能：将单元及节点数据写入后处理文件
	* 输入：文件名，数据内容名，数据，数据类型：标量，矢量，张量，当前时间步
	* 输出：无
	'''
	# 以追加的方式写入原来网格文件的末尾
	mshfile = "%s.msh" % filename
	f = open(mshfile,'a')
	# 设置打印样式为小数点后8位
	np.set_printoptions(formatter={'float_kind':'{:.8f}'.format})
	# 写入节点值数据
	num = data.shape[0]
	# 数据头
	f.writelines("$NodeData\n1\n\"%s\"\n1\n%d\n3\n%d\n%d\n%d\n" % (postname,timestep,timestep,order,num-1))
	# 节点数据，注意[1:-1]是为了去掉数组字符串化后的中括号
	f.writelines(['%d %s\n' % (x,str(data[x])[1:-1]) for x in xrange(1,num)])
	# 结束写入结束标记
	f.writelines("$EndNodeData\n")
	f.close()
	return