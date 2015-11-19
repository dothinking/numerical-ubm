lc = 0.18;
Point(1) = {0, 0, 0, lc};
Point(2) = {0, 8, 0, lc};
Line(1) = {1,2};
surfs[] = Extrude {20,0,0} { Line{1}; Layers{{20/lc}, {1}};};
// surfs[] = Extrude {20,0,0} { Line{1};};
// Recombine Surface{surfs[1]};