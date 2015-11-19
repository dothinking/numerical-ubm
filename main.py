# encoding: utf8
import prepostprocessing as pro
import solving as slv
import numpy as np
from sympy import *
import math
import sys
import os

if __name__ == '__main__':
	
	R0 = 7.985 # 初始半径
	R1= 6.625 # 锻后半径
	FEED = 0.37 # 送尽量
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
		len_forging_zone = (R0-R1)/k - FEED # 锻造区理论长度
		X0 = R0 / k # 锻造区右边界点
		X1 = X0 - len_forging_zone # 锻造区左边界点
		X2 = X1 - FEED # 整形区左边界点

		post_disp = np.zeros_like(NODES) # 节点位移
		post_strain = np.zeros((NODES[0][0]+1,1)) + 0.1 # 节点等效应变值

		for i in range(0,4):
			current_feed = FEED * i			

			# 局部坐标系下当前坐标
			nodes = NODES + post_disp
			nodes[1:,0] += X0 - current_feed # 变换到局部坐标系

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

			print np.sum(slv.area_integral(strain_fun,ELEMENTS,nodes,post_strain,forging_eles,1))
			sys.exit(0)