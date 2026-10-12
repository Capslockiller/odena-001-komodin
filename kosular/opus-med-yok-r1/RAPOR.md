# RAPOR — Molly's Nightstand

`sonuc.blend` → collection **Molly's Nightstand**. Metres, floor at Z=0, front faces −Y. No materials (the factory default material was removed too).
Scripts: `build.py` builds the model, `render_preview.py` renders the Workbench previews into `preview/` (front, side, top, two 3/4 views).

## Overall size
43 × 43 cm (the top), 39 × 39 cm at the widest point of the body, **80.0 cm** total height. Body 8–75.7 cm, top 75.5–80 cm, legs 0–9 cm (the top 1 cm sits inside the body).

## Parts and modifiers
| Part | How it was built | Modifiers |
|---|---|---|
| `Body` | Lofted from 55 rounded-square sections. The half-width follows a profile w(z): 32.6 cm at the bottom, **39 cm max at ~62 % of the height**, 37.8 cm at the top. Plan corner radius 3 cm, 8 mm round on the bottom edge. | none (the geometry is final). Shade smooth by angle at 40° |
| `Top` | Lofted from the same kind of section: 8 mm chamfer on the bottom edge, straight band, 22 mm quarter round on the top edge. Plan corner radius 4.5 cm. | Bevel (angle limit 30°, 1.5 mm, 2 segments) softens the chamfer edges |
| `Drawer_Front`, `Door` | A rounded-rectangle panel outline (1.6 cm radius), sliced into horizontal and vertical strips and then wrapped onto the body: its width follows the body (3.4 cm side margin) and its depth follows the bulge. The face sits 8 mm proud of the body. Drawer 20.3 cm, door 40.6 cm (2×), 6 mm gap. | Solidify (11 mm, toward the inside, even thickness) → Bevel (angle 50°, 3.5 mm, 3 segments) |
| `Knob_Drawer`, `Knob_Door` | A half-profile (spindle + flattened mushroom head, Ø3.9 cm, 2.8 cm deep) made from edges. Each knob is placed at the centre of its panel and aligned to the surface normal of the bulging front at that height. | Screw (360°, 40 steps, merge on axis) |
| `Leg_FL/FR/BL/BR` | Lofted from rounded-square sections (corner radius 55 % of the half-width, so they read as nearly round). 5.8 cm at the top tapering to 4.4 cm, 4 mm round at the foot, centres at ±12.7 cm. | none. Shade smooth by angle |

Hierarchy: the knobs are parented to their panels, and the other parts are parented to `Body`.

## Method
Everything is procedural (bmesh plus a few modifiers), driven by a single body profile function w(z). The panels and knobs read the same function, so they follow the bulge and taper of the body exactly. Mesh-wise, the loft gives the body clean quad rings with no stretched Subdivision artefacts. The parts that a modeller would normally build with modifiers (panel thickness and edge softening, knobs from a lathe) were done with modifiers, and those modifiers stay live (not applied).

## Where the brief left me guessing
- **"Bombeli" (bulge):** I interpreted it as a vertical-profile bulge only. The side faces have no horizontal curvature, so the plan is straight-sided with rounded corners. The bulge size (±1.6 cm from the widest point) and the 62 % height of the widest point are my choices.
- **Legs:** the brief does not say square or round. I used a rounded section between the two. Leg height (8 cm visible) and thickness are estimates of "short and thick".
- **Top:** overhang of 2 cm all round from the widest point of the body (about 2.6 cm at the top edge). Thickness 4.5 cm. Edge radius and chamfer sizes are estimates.
- **Panels:** the brief does not say whether the panel edges should follow the taper or stay vertical. I made them follow the body taper, which matched the cartoon look. The side margin, proud distance (8 mm) and gap (6 mm) are estimates.
- **Bottom of the body:** the brief does not say whether there is a plinth or apron below the door. I left a 3.2 cm plain strip of body there.
- **Door hinge side and drawer box:** neither is described, so they were not modelled. The fronts are single panels and there is no interior.
- **Knob size:** "küçük" (small) was taken as Ø3.9 cm, with a short 5 mm visible spindle.
