# Molly's Nightstand - Project Report

## Parts
The model is organized inside the `Molly's Nightstand` collection and consists of the following objects:
- **Body**: The main cabinet body.
- **TopPlate**: The thick, overhanging top board.
- **Drawer**: The upper front panel (squat).
- **Door**: The lower front panel (taller).
- **Drawer_Handle_shaft** & **Drawer_Handle_knob**: Handle components for the drawer.
- **Door_Handle_shaft** & **Door_Handle_knob**: Handle components for the door.
- **Leg_FL**, **Leg_FR**, **Leg_BL**, **Leg_BR**: The four tapering legs at the bottom corners.

## Modifiers per Part
- **Body**: `Bevel` (to soften the 4 vertical corners).
- **TopPlate**: None. (Beveling was done procedurally via BMesh to allow different profiles for the vertical corners, top edge, and bottom edge).
- **Drawer**: `Bevel` (to create soft edges for the panel).
- **Door**: `Bevel` (to create soft edges for the panel).
- **Legs**: `Bevel` (to slightly soften the bottom resting edge).
- **Handles**: None (modeled directly with smooth shading).

## Chosen Method
I wrote a headless Python script using Blender's `bpy` and `bmesh` APIs. To achieve the specific "swollen in the middle, narrowing at the bottom" look while ensuring the front drawer/door panels perfectly track this curve, I used a procedural approach:
1. Created high-resolution box meshes for the body and the front panels by applying a temporary `Subsurf` modifier.
2. Iterated over the vertices and displaced them using a quadratic mathematical function (a parabola mapped to the Z-axis) to create the exact bulging profile. This ensured the body's front face and the protruding drawer/door panels share the exact same mathematical curvature.
3. Used BMesh tools to bevel the `TopPlate` with custom settings (plump top rim, chamfered bottom rim).
4. Added `Bevel` modifiers to the main objects to non-destructively soften the remaining sharp edges.
5. Saved `sonuc.blend` with pure geometry, then dynamically added a camera and lighting to render `preview.png` for verification.

## Where the Brief Left Me Guessing
- **Exact Curve Profile:** "Ortada biraz şişkin, aşağı doğru belirgin şekilde daralıyor" is descriptive but not numerically precise. I assumed a parabolic curve that peaks just below the middle and tapers heavily towards the bottom.
- **Top Plate Overhang & Thickness:** I assumed a 5cm thick plate with a slight overhang (max width 40x40cm).
- **Knob Proportions:** Modeled them as icospheres squashed on the Y-axis to fit "basık topuz kulp" (squashed knob).
- **Leg Angles/Positions:** Placed them vertically near the corners. The brief didn't specify if they splay outward, so they were kept straight down but tapered.
- **Panel Gap:** Left a 1cm gap between the drawer and the door to ensure a clean "ince bir boşluk".
