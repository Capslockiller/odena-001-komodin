# Molly's Nightstand — Rapor

`sonuc.blend` holds 10 objects, all in the `Molly's Nightstand` collection. There are no materials. The model is built in metres with the origin at the floor centre, and the front faces −Y.
Overall size: 0.44 × 0.44 × 0.80 m at the top slab. The body is 0.34–0.40 m wide. Measured on the evaluated geometry, the knobs add about 1.6 cm at the front.

## Parts and modifiers

| Part | Description | Modifiers |
|---|---|---|
| `Body` | Square-plan carcass, z 0.10–0.755. Rounded vertical corners (R 3 cm). Width 34 cm at the bottom, 40 cm at the bulge (62 % of the height) and 38.5 cm at the top. The same profile is used on all four sides. | Bevel (6 mm, 3 seg, angle-limited: softens only the top and bottom rims), Weighted Normal |
| `Top` | Slab 44 × 44 × 4.5 cm with corner radius R 5 cm. It overhangs the body by about 2.75 cm on every side. The upper edge has a 22 mm quarter-round; the lower edge has an 8 × 7 mm chamfer. | Weighted Normal (the profile is in the geometry) |
| `Drawer_Front` | z 0.545–0.725 (18 cm) | Bevel (5 mm, 4 seg, angle-limited), Weighted Normal |
| `Door` | z 0.177–0.537 (36 cm = 2 × the drawer), with an 8 mm gap to the drawer | same as the drawer |
| `Knob_Drawer`, `Knob_Door` | Shaft (Ø 12 mm) and a flattened knob (Ø 44 mm) turned as one profile. Each sits at the centre of its panel, with its axis tilted to follow the surface normal of the bulge. | Subdivision (1 viewport / 2 render) |
| `Leg_FL/FR/BL/BR` | 10 cm tall with rounded-square sections, 6 cm at the top tapering to 4.4 cm at the bottom. They sit near the corners, and their tops sink 6 mm into the body. | Bevel (4 mm, 3 seg), Weighted Normal |

## Method
- Procedural modelling with a Python script (`model.py`): bmesh plus a few modifiers. `render.py` produces the Workbench previews in `onizleme/`.
- The body and the top are **lofted** from stacked rounded-square rings. For the body, a width function `w(z)` (two half-parabolas meeting at the bulge peak) sets the size of each ring, so the bulge and the downward taper live in the geometry. For the top, a profile of (inset, z) points produces the round upper edge and the chamfered lower edge.
- The panels are built as a grid on the same `w(z)` function: the front face sits 10 mm proud of the body, and the back is embedded 3 mm. This makes the panels follow the bulge exactly in both depth and width (they narrow towards the bottom with the body). An angle-limited Bevel softens only their outer edges.
- The knobs are lathed (a revolve of one profile).
- Shading uses smooth-by-angle plus Weighted Normal. Subdivision is used only on the knobs, so the dimensions stay exact.

## Where the brief left me guessing
- **Drawer/door proportions vs. "basık":** with a 1 : 2 ratio, filling the whole front makes the drawer about 19 cm tall, which is not really flat. I chose 18 cm and 36 cm instead, which leaves a plain apron of about 7.7 cm under the door.
- **Bulge amount and position:** "slight bulge, clearly narrowing downwards" became 40 cm at the widest point, 34 cm at the bottom and 38.5 cm at the top, with the peak at about 62 % of the height. I assumed the front and back follow the same profile as the sides.
- **Top thickness and overhang:** "thick" became 4.5 cm. "Overhangs a little" became about 2.75 cm at the top of the body.
- **Leg height and section:** "short, thick" became 10 cm tall with a 6 → 4.4 cm square section. I chose a rounded-square section; round legs would also fit the brief.
- **Panel side margins, knob size and shaft length:** these were estimated by eye (4.2 cm margins, Ø 44 mm knobs).
- The drawer is modelled only as a front panel; there is no interior or drawer box, because the brief describes only the exterior.

## Check
I rendered front, side, top and two perspective views. The bulge, the downward taper, the overhang, the edge profiles, the 1 : 2 panels, the gap, the knobs and the tapered legs all match the brief. The first renders showed the drawer as too tall for "basık", so I fixed that in the proportions described above.
