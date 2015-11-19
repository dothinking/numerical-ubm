# encoding: utf8
###############################################################
# 功能：计算相关函数
# 作者：Train
# 日期：2014-12-24
###############################################################
import math
import numpy as np
from sympy import *

z,r = symbols('z,r')

def velocity_field(sym_stream_function,z,r):
	'''
	* 功能：根据流函数计算速度场
	* 输入：流函数、两个维度的变量，输入应为Symbols变量
	* 输出：速度场符号表达式列表
	'''
	vz = -diff(sym_stream_function,r) / r
	vr = diff(sym_stream_function,z) / r
	return vz,vr

def plastic_strain_rate(sym_vz,sym_vr,z,r):
	'''
	* 功能：根据速度场计算等效塑性应变率
	* 输入：轴向速度、径向速度、坐标分量
	* 输出：节点等效塑性应变符号表达式
	'''
	strain_rate_r = diff(sym_vr,r)
	strain_rate_z = diff(sym_vz,z)
	strain_rate_sita = -(strain_rate_r+strain_rate_z)
	strain_rate_rz = 0.5 * (diff(sym_vr,z)+diff(sym_vz,r))
	strain_rate = sqrt(2.0/3.0*(strain_rate_r**2 + strain_rate_z**2 + strain_rate_sita**2 + 2.0*strain_rate_rz**2))
	return strain_rate

def strain_function(sym_strain_rate):
	'''
	* 功能：面积分所用单元被积函数
	* 输入：等效塑性应变符号表达式
	* 输出：节点函数值符号函数
	'''
	S = 2.0*pi*r*sym_strain_rate
	return lambdify((z,r),S,'numpy')

def fun_flow_stress(ps):
	'''
	* 功能：流动应力模型
	* 输入：等效塑性应变
	* 输出：流动应力值
	'''
	return 618.14*ps**0.1184

def fun_area_integral(sym_fun,elements,nodes,strain,ele_id,order=1):
	'''
	* 功能：三角形单元积分
	* 输入：被积函数（符号表达式），单元数组，节点坐标数组，节点应变数组，积分区域单元，积分点阶次
	* 输出：单元积分值
	'''
	### 当前积分单元所有节点坐标
	ele_nodes = nodes[elements[ele_id]]
	# print ele_nodes
	ele_strain = strain[elements[ele_id]]
	### 计算三角形单元面积
	#根据三角形单元顶点坐标计算单元面积
	#        |1 x1 y1|    /
	#  V =   |1 x2 y2|   /   2
	#        |1 x3 y3|  /
	area = np.ones((3,3),np.float)
	area[:,1:] = ele_nodes[:,0:-1]
	area_ele = abs(np.linalg.det(area)) / 2.0 # 防止编号顺序相反导致面积为负
	### 根据自然坐标系积分点计算全局积分点
	# 积分点面积坐标
	local_lib = np.array([
			[1.0/3.0, 1.0/3.0, 1.0/3.0],
			[2.0/3.0, 1.0/6.0, 1.0/6.0], 
			[1.0/6.0, 2.0/3.0, 1.0/6.0], 
			[1.0/6.0, 1.0/6.0, 2.0/3.0], 
			[1.0/3.0, 1.0/3.0, 1.0/3.0], 
			[3.0/5.0, 1.0/5.0, 1.0/5.0], 
			[1.0/5.0, 3.0/5.0, 1.0/5.0],
			[1.0/5.0, 1.0/5.0, 3.0/5.0]
		])
	# 积分点对应权系数
	weight_lib = [[1],[1.0/3.0, 1.0/3.0, 1.0/3.0],[-27.0/48.0, 25.0/48.0, 25.0/48.0, 25.0/48.0]]
	# 根据积分阶次选择积分点及权系数
	if order == 2:
		local = local_lib[1:4,:]
		weight = np.array(weight_lib[1])
	elif order == 3:
		local = local_lib[4:,:]
		weight = np.array(weight_lib[2])
	else:
		local = local_lib[0,:]
		weight = np.array(weight_lib[0])
	# 计算全局坐标系积分点
	int_nodes = np.dot(local,ele_nodes)	
	int_nodes.shape = (-1,3) # 单积分点时也强制转为二维数组，避免维度不匹配
	# 计算积分点等效塑性应变值
	int_strain = np.dot(local,ele_strain)
	int_strain.shape = (-1,1)
	### 计算积分点函数值
	# val_strain = plastic_work(sym_strain,int_nodes[:,0],int_nodes[:,1],int_nodes[:,2]) # 应变
	val_strain = sym_fun(int_nodes[:,0],int_nodes[:,1])
	val_stress = flow_stress(int_strain[:,0]) # 应力
	val_nodes = val_strain * val_stress
	### 计算单元积分值
	val_ele = np.dot(val_nodes,weight)
	res = val_ele * area_ele
	return res

# 函数向量化，以提高计算效率
flow_stress = np.vectorize(fun_flow_stress)
area_integral = np.vectorize(fun_area_integral)
# fun_area_integral函数中常量数组（如总单元、节点、应变）无需向量话，因此排除之，参考vectorize()函数的excluded参数说明：
# excluded : set, optional
# Set of strings or integers representing the positional or keyword arguments for which the function will not be vectorized. 
# These will be passed directly to pyfunc unmodified.
# New in version 1.7.0.
area_integral.excluded.add(1)
area_integral.excluded.add(2)
area_integral.excluded.add(3)