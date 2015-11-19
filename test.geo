lc = 0.2;
		R = 7.985;
		L = 25;
		Point(1) = {0, 0, 0, lc};
		Point(2) = {0, R, 0, lc};
		Line(1) = {1,2};
		ex[] = Extrude {L,0,0} { Line{1}; Layers{{L/lc}, {1}};};
		Physical Volume(1) = ex[1];