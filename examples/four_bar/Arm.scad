module rod(a, b, r, n_facets) {
    dir = b-a;
    h   = norm(dir);
    if (dir[0] != 0 && dir[1] != 0)
    {
        w=b-a;
        cylinder(r=r, h=h, $fn=n_facets);
    } 
   if (dir[0] != 0 || dir[1] != 0) {
        w  = dir / h;
        u0 = cross(w, [0,0,1]);
        u  = u0 / norm(u0);
        v0 = cross(w, u);
        v  = v0 / norm(v0);
        multmatrix(m=[[u[0], v[0], w[0], a[0]],
                      [u[1], v[1], w[1], a[1]],
                      [u[2], v[2], w[2], a[2]],
                      [0,    0,    0,    1]])
        cylinder(r=r, h=h, $fn=n_facets);
    }
}

n_facets=20;
rod_r=0.03;
r=rod_r;
r_in=0.1;
d=0.2;
l=3.05;
a=[0,-r_in,0];
b=[0,-d,0];
c=[+d,-d,0];
D=[+d,0,0];
e=[+l,0,0];

union(){
    // union(){
        // union(){
            // union(){
                // union(){
                   // union(){
                        rod(a, b, r, n_facets);
                        translate(b) sphere(r=r,$fn=n_facets);
                   // }
                    rod(b, c, r, n_facets);
                // }
                translate(c) sphere(r=r,$fn=n_facets);
            // }
            rod(c, D, r, n_facets);
       //  }
        translate(D) sphere(r=r,$fn=n_facets);
   //  }
    rod(D, e, r, n_facets);
}


