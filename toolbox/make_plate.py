"""Generate switch mounting plate designs."""

import shapely
import shapely.geometry

from toolbox.outline import generate_outline, shapely_round

# Polygon describing the shape of an individual key cutout
cutout_geom_mx = shapely.geometry.polygon.Polygon([
    # untested
    (7, 7),
    (7, -7),
    (-7, -7),
    (-7, 7),
])
cutout_geom_mx_alps = shapely.geometry.polygon.Polygon([
    # from https://github.com/swill/kad/blob/62948e9/key.go
    # untested
    (7, -7),
    (7, -6.4),
    (7.8, -6.4),
    (7.8, 6.4),
    (7, 6.4),
    (7, 7),
    (-7, 7),
    (-7, 6.4),
    (-7.8, 6.4),
    (-7.8, -6.4),
    (-7, -6.4),
    (-7, -7),
])
cutout_geom_mx_wings = shapely.geometry.polygon.Polygon([
    # adapted from https://github.com/swill/kad/blob/62948e9/key.go
    (7, -7),
    (7, -6),
    (7.8, -6),
    (7.8, -2.9),
    (7, -2.9),
    (7, 2.9),
    (7.8, 2.9),
    (7.8, 6),
    (7, 6),
    (7, 7),
    (-7, 7),
    (-7, 6),
    (-7.8, 6),
    (-7.8, 2.9),
    (-7, 2.9),
    (-7, -2.9),
    (-7.8, -2.9),
    (-7.8, -6),
    (-7, -6),
    (-7, -7),
])
cutout_geom_alps = shapely.geometry.polygon.Polygon([
    # adapted from https://github.com/swill/kad/blob/62948e9/key.go
    # untested
    (7.8, -6.4),
    (7.8, 6.4),
    (-7.8, 6.4),
    (-7.8, -6.4),
])


def generate_hole_shape(center, diameter):
    return center.buffer(diameter / 2)


def cherry_stabilizer(length):
    offsets_by_size = {
        # adapted from https://github.com/swill/kad/blob/62948e9/key.go
        0: None,
        2: 11.9,
        #3: 19.05,
        #4: 28.575,
        #4.5: 34.671,
        #5.5: 42.8625,
        6: 47,
        #6.25: 50,
        #6.5: 52.38,
        #7: 57.15,
        #8: 66.675,
    }

    # find appropriate offset
    s = offsets_by_size[max(x for x in offsets_by_size.keys() if x <= length)]
    if not s:
        return None

    stab_path = shapely.geometry.polygon.Polygon([
        # adapted from https://github.com/swill/kad/blob/62948e9/key.go
        (s - 3.375, 2.3),
        (s - 3.375, 5.53),
        (s + 3.375, 5.53),
        (s + 3.375, 2.3),
        (s + 4.2, 2.3),
        (s + 4.2, -0.5),
        (s + 3.375, -0.5),
        (s + 3.375, -6.77),
        (s + 1.65, -6.77),
        (s + 1.65, -7.97),
        (s - 1.65, -7.97),
        (s - 1.65, -6.77),
        (s - 3.375, -6.77),
        (s - 3.375, -2.3),
        (-s + 3.375, -2.3),
        (-s + 3.375, -6.77),
        (-s + 1.65, -6.77),
        (-s + 1.65, -7.97),
        (-s - 1.65, -7.97),
        (-s - 1.65, -6.77),
        (-s - 3.375, -6.77),
        (-s - 3.375, -0.5),
        (-s - 4.2, -0.5),
        (-s - 4.2, 2.3),
        (-s - 3.375, 2.3),
        (-s - 3.375, 5.53),
        (-s + 3.375, 5.53),
        (-s + 3.375, 2.3),
    ])

    return stab_path
    # if vertical {


# 	stab_path.RotatePath(90, Point{0, 0})
# }
# if flip_stab {
# 	stab_path.RotatePath(180, Point{0, 0})
# }
# if key.RotateStab != 0 {
# 	stab_path.RotatePath(key.RotateStab, Point{0, 0})
# }

# stab_path.Rel(c)
# if ctx.RotateCluster != 0 {
# 	stab_path.RotatePath(ctx.RotateCluster, Point{ctx.Xabs*k.U1 + k.DMZ + k.LeftPad, ctx.Yabs*k.U1 + k.DMZ + k.TopPad})
# }
# k.Layers[SWITCHLAYER].CutPolys = append(k.Layers[SWITCHLAYER].CutPolys, stab_path)


def generate_cherry_cutout(key, corner_radius=0.3, resolution=16):
    x, y, r = key.pose.x, key.pose.y, key.pose.r
    shape = cutout_geom_mx

    # add stabilizers along the long axis of key
    if key.unit_height == 1 and key.unit_width > 1:
        stab_geom = cherry_stabilizer(key.unit_width)
        if stab_geom:
            shape = shape.union(stab_geom)
    elif key.unit_width == 1 and key.unit_height > 1:
        stab_geom = cherry_stabilizer(key.unit_height)
        if stab_geom:
            shape = shape.union(stab_geom)
        shape = shapely.affinity.rotate(shape, -90)
    else:
        pass  # TODO: warn about unusual size

    shape = shapely.affinity.rotate(shape, r)
    shape = shapely.affinity.translate(shape, x, y)

    return shapely_round(shape,
                         corner_radius,
                         corner_radius,
                         resolution=resolution).exterior


def generate_plate(kb, padding=0, mounting_holes=False):
    features = []

    for key in kb.keys:
        features.append(generate_cherry_cutout(key))

    if mounting_holes:
        for h in kb.hole_positions:
            center = shapely.geometry.Point(h.x, h.y)
            features.append(
                generate_hole_shape(center, kb.hole_diameter).exterior)

    outline = generate_outline(kb)
    return shapely.geometry.polygon.Polygon(outline, holes=features)
