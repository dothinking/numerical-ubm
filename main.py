# encoding: utf8
import prepostprocessing as pro
import solving as slv
import numpy as np
from sympy import *
import math
import sys
import os

def f(x):
	return x+1,x+2,x+3

if __name__ == '__main__':

	x = np.array([[1,2,5],[2,3,5],[3,4,5],[2,3,6]])


	fun = np.frompyfunc(f,1,3)
	t = fun(np.array([10,20,30]))

	a = np.zeros((4,3))
	print a

	a[1:4] = np.array(t).T

	print a


	sys.exit(0)

	R0 = 7.985 # 初始半径
	R1= 6.625 # 锻后半径
	N = 5 # 计算步数
	ALPHA = 4.3 # 锤头锥角
	LENGTH = 25 # 坯料长度

	pname = "test"
	ele_size = 0.2 # 网格尺寸

	if not pro.generate_mesh(pname,R0,LENGTH,ele_size):
		sys.exit(0)
	else:		
		ELEMENTS,NODES = pro.read_elements(pname,2)

	alpha = math.radians(ALPHA)
	k = math.tan(alpha)		
	h = (R0-R1)/N
	FEED = h/k
	X0 = R0/k

	# 变换到局部坐标系
	nodes = NODES.copy()
	nodes[:,0] += X0

	# 后处理数据
	post_disp = np.zeros_like(NODES) # 节点位移
	post_strain = np.zeros((NODES[0][0]+1,1)) + 0.1 # 节点等效应变值

	for i in range(0,N):

		current_feed = FEED * i

		# 优化计算

		# 确定变形区节点
		all_nids = np.arange(1,int(NODES[0][0])+1)
		rigid_l_ids = all_nids[nodes[1:,0]<X2]
		sizing_ids = all_nids[np.logical_and(nodes[1:,0]>=X2,nodes[1:,0]<X1)]
		forging_ids = all_nids[np.logical_and(nodes[1:,0]>=X1,nodes[1:,0]<=X0)]
		rigid_r_ids = all_nids[nodes[1:,0]>X0]

		# 锻造区、整形区单元集合
		sizing_eles = pro.belongs_to_element(ELEMENTS,sizing_ids)
		forging_eles = pro.belongs_to_element(ELEMENTS,rigid_r_ids)

		r,z = symbols('r,z')
		zn = symbols('zn',positive=True)
		stream_function = -0.5/k*(1-zn**2/z**2)*r**2
		vz,vr = slv.velocity_field(stream_function,z,r)
		ps = simplify(slv.plastic_strain_rate(vz,vr,z,r))
		strain_fun = slv.strain_function(ps)



		# 更新坐标
		nodes = NODES + post_disp
		# 更新局部坐标系
		nodes[:,0] -= FEED

		
		print np.sum(slv.area_integral(strain_fun,ELEMENTS,nodes,post_strain,forging_eles,1))
		sys.exit(0)
