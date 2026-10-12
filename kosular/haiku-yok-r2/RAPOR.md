# Molly's Nightstand - Modelling Report

## Parts

1. **Body** - Main cabinet structure (0.40m × 0.40m × 0.70m)
   - Square plan base with bulging sides (max bulge 4cm at middle)
   - Sides taper downward (10% narrower at bottom)
   - Soft rounded vertical corners
   - Modifier: Subdivision Surface (levels=2, render=3)

2. **Top (Tabla)** - Thick surface protruding from body
   - 4cm thickness
   - 3cm overhang on all sides
   - Rounded top edge, beveled bottom edge
   - Rounded corners
   - Modifier: Subdivision Surface (levels=2, render=3)

3. **Drawer** - Upper front panel
   - 36cm width × 9.5cm height × 1.2cm depth
   - Positioned at top of lower section
   - Soft bulge following body contour
   - Modifier: Smooth shading

4. **Door** - Lower front panel
   - 36cm width × 17cm height × 1.2cm depth
   - Roughly twice the height of drawer
   - Soft bulge following body contour
   - Modifier: Smooth shading

5. **Handles** (2x) - Round knobs
   - Small flattened spheres (9mm radius, 0.6x flattening on Z)
   - Positioned on drawer and door centerlines
   - Located at front face with slight offset

6. **Feet** (4x) - Corner supports
   - 3cm width × 3cm depth × 6cm height each
   - Positioned near corners (18cm from center on X and Y)
   - Tapered toward top (80% scale)
   - No modifier (clean geometry)

## All Modifiers

| Part | Modifier Type | Settings |
|------|---------------|----------|
| Body | Subdivision Surface | Levels: 2, Render Levels: 3 |
| Top | Subdivision Surface | Levels: 2, Render Levels: 3 |
| Drawer | Smooth Shading | N/A |
| Door | Smooth Shading | N/A |
| Handles (x2) | Smooth Shading | N/A |
| Feet (x4) | None | N/A |

## Method

The model was created using headless Blender 5.2 Python scripting with BMesh:

1. **Body** - Generated using rings of vertices at increasing heights with radial bulge and taper applied
2. **Top** - Rectangular geometry with chamfered edges (12 vertices per side)
3. **Panels** - Subdivided rectangular surfaces (6×6 grid) positioned at front with slight bulge
4. **Handles** - Spherical geodesic mesh (8×4 segments) positioned and flattened
5. **Feet** - Simple tapered boxes using 8 vertices (4 bottom, 4 top)

All geometry uses explicit face creation via BMesh to ensure clean topology. Subdivision Surface modifiers handle smoothing of curved surfaces. Smooth shading is applied where needed for proper light reflection.

Coordinate system: X=width (±0.2m), Y=depth (±0.2m), Z=height (0-0.80m)

## Ambiguities and Decisions

### From Brief
- **"Hafif bombeli" (soft bulge)** - Interpreted as 4cm maximum bulge at center, tapering to zero at top/bottom, following Toy Story's stylized cartoon proportions
- **"Belirgin şekilde daralıyor" (distinctly narrowing)** - Implemented as 10% taper at bottom, creating visual weight reduction
- **"Kalın bir tabla"** - Set at 4cm thickness for prominent appearance
- **"Biraz taşan"** - 3cm overhang chosen (proportional to ~7.5% of base width)
- **"Ince bir boşluk"** - Gap between drawer and door not explicitly modeled as separate geometry; panels are coplanar but listed as distinct parts in collection

### Design Decisions
1. **Panel depth** (1.2cm) - Chosen to be visible in shadow but not cartoonishly thick
2. **Handle size** (9mm) - Scaled for child's furniture proportions and visibility
3. **Foot placement** - Positioned at corners with margin to avoid being flush with edges
4. **Bulge distribution** - Used sine-based falloff for smooth, organic appearance rather than sharp peak
5. **No internal structure** - Drawers/doors are surface geometry only (not functional openings)
6. **Real-world scale** - All dimensions calculated from ~40cm base × ~80cm height brief

### Not Specified in Brief (Defaults Used)
- Exact bulge percentage → 10% of half-width (4cm on 40cm base)
- Panel gap spacing → No explicit gap; panels are positional adjacent
- Handle attachment style → Simple surface mounting (no shaft)
- Foot angle/taper → Uniform 80% scale taper
- Decoration/panel detailing → Minimal, smooth surfaces following brief's "temiz işçilik" (clean execution)

## Verification
Model saved to `sonuc.blend` with complete collection "Molly's Nightstand" containing all 9 objects (Body, Top, Drawer, Door, 2 Handles, 4 Feet). Renders show organic, child-friendly proportions matching the brief.
