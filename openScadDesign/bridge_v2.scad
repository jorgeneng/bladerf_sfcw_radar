x_base = 160*2;
y_base = 40;
z_base = 6;

rail_lenth = 70;
x_displace = x_base/2-10-rail_lenth/2;
y_displace = 10;
r_hole=3;

difference(){
    cube([x_base,y_base,z_base],center=true);
    translate([x_displace,y_displace,0])
        cube([rail_lenth,r_hole*2,z_base+1],center=true);
    translate([x_displace,-y_displace,0])
        cube([rail_lenth,r_hole*2,z_base+1],center=true);
    translate([-x_displace,y_displace,0])
        cube([rail_lenth,r_hole*2,z_base+1],center=true);
    translate([-x_displace,-y_displace,0])
        cube([rail_lenth,r_hole*2,z_base+1],center=true);
}

//handle
x_handle = 40;
y_handle = 40;
z_handle = 40;
r_handle_hole = 10;
translate([0,0,z_handle/2-0.001])
//difference(){
//    intersection(){
//        cube([x_handle,y_handle,z_handle],center=true);
//        rotate([90,0,0])
//        cylinder(h=40,r=r_handle_hole*2,center=true);
//
//    }
//    rotate([90,0,0])
//    cylinder(h=42,r=r_handle_hole,center=true);
//}

difference(){
    union(){
    translate([0,0,-z_handle/4+0.001])
    cube([x_handle,y_handle,z_handle/2],center=true);
    
    rotate([90,0,0])
    cylinder(h=40,r=r_handle_hole*2,center=true);
    }
    rotate([90,0,0])
    cylinder(h=42,r=r_handle_hole,center=true);
}

