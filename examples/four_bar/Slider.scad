r_out=0.1;
height=0.3;
r_in=0.07;
n_facets=20;

difference(){
translate([0,0,-0.3/2]) cylinder(r=r_out, h=height, $fn=n_facets);
translate([0,0,-0.3/2]) cylinder(r=r_in, h=height, $fn=n_facets);
}