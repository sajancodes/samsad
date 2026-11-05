# SAMSAD — Authentic 3D Nepali Character Models & Cache-Busting Overhaul Plan

## 1. Why the Old 3D Characters Appeared in Your Screenshots
1. **Browser Static Asset Caching (`maxAge: '1h'`)**: `server.ts` had `maxAge: '1h'` enabled and `index.html` loaded `/assets/main-CfQ2THv5.js` and `/assets/main-C4DN45Lw.css` without a cache-busting query string, causing the browser to display the cached earlier version (which is why *"Diwali pe mithai khilao"* and the old hall emblem were still visible).
2. **Base `.glb` Geometry & Unwired `facePhoto` Property**:
   - In `main-CfQ2THv5.js`, `P[charId].facePhoto` was not defined on the fighter objects, so `setFacePhoto()` was never triggered on the character select screen.
   - More importantly, the base `.glb` files (`yogi.glb`, `didi.glb`, `modi.glb`, `rahul.glb`, `trump.glb`) have the old Indian politicians' 3D clothes, hair, and beards sculpted directly into their meshes (`yogi.glb` is a bald monk in a saffron dhoti, `didi.glb` wears a female sari and earrings, `modi.glb` and `rahul.glb` have white 3D beards, and `trump.glb` has bright yellow hair).

---

## 2. Full 3D Nepali Character Asset Overhaul (All 9 Fighters)

We will build a dedicated **3D Nepali Character Sculptor & Mesh Overhaul (`buildNepali3DCharacter`)** that runs automatically on every fighter's 3D rig (`ml` constructor and `setFacePhoto`) and transforms both the **3D body meshes/outfits** and the **3D head, face, hair, beard, eyewear, and headgear**:

| Fighter | Old `.glb` Issue Fixed | New 3D Nepali Character Asset & Appearance |
| :--- | :--- | :--- |
| **KP Baa** (`modi`) | Had Modi's white 3D beard & saffron vest | **Clean-shaven chin with grey mustache**, **3D geometric Nepali Dhaka Topi**, **round prescription glasses**,KP Oli's 3D contoured face texture, and **charcoal Nepali Daura Suruwal + black waistcoat**. |
| **Balen** (`yogi`) | Was a bald monk in a saffron `Dhoti` & `Shawl` | **Strips saffron dhoti/shawl**, converts body to **sharp pitch-black blazer/suit & dark trousers**, adds **3D thick dark curly hair + full dark beard**, **signature black rectangular sunglasses**, and **black Nepali Dhaka/Bhadgaunle Topi**. |
| **Harka** (`didi`) | Was a female mesh in a `Sari`, `Blouse`, `HairBun` & `Earrings` | **Swaps to male athletic trouser/shirt rig** (removes `Sari`, `Earrings`, and `HairBun`), adds **short dark hair**, **Dharan sky-blue Shramdaan track jacket & dark work pants**, and Harka Sampang's 3D face. |
| **Prasai Dai** (`trump`) | Had Trump's yellow hair, red tie & Trump face | **Recolors hair to dark salt-and-pepper**, adds **thick dark mustache + prominent crimson Tika on forehead**, Durga Prasai's 3D face texture, and **dark maroon/charcoal Nepali coat**. |
| **Gagan** (`rahul`) | Had Rahul Gandhi's thick white beard | **Removes white beard**, adds **youthful Gagan Thapa 3D face**, **dark wavy parted hair**, **modern rectangular glasses**, and **emerald-green Congress waistcoat over crisp white kurtha**. |
| **Deuba Daju** (`nitin`) | Had Nitin Gadkari's face & vest | **Tall traditional Nepali Dhaka Topi**, Sher Bahadur Deuba's 3D face texture, and **formal grey Nepali Congress coat over Daura Suruwal**. |
| **Rabi Dai** (`ravi`) | Had generic dark vest | **Neat dark TV-anchor parted hair**, Rabi Lamichhane's 3D face texture, and **RSP Bell-Blue waistcoat & sky-blue shirt**. |
| **Prachanda** (`lalu`) | Had Lalu's hair & white kurta | **Swept-back silver/grey 3D hair**, **bushy white/grey mustache**, **glasses**, Prachanda's 3D face texture, **dark formal charcoal suit**, and **crimson Maoist tie**. |
| **Gen-Z Boss** (`mbapu`) | Had bald Bapu mesh | **Dark streetwear protest hoodie**, **3D One Piece Straw Hat** with red ribbon, **glowing neon protest visor/shades**, and Gen-Z leader 3D face. |

---

## 3. How the 3D Face & Head Overhaul Works Technically
1. **Wire `facePhoto` on All 9 Character Definitions (`P[id].facePhoto`)**:
   - Set `facePhoto: "/faces/" + id + ".webp?v=20261105_samsad3d"` on every character in `P` and preload all 9 textures at boot so both the **Character Select 3D stage** and **In-Fight 3D Rigs** always have the texture ready immediately.
2. **3D Contoured Face Shield + Head Feature Sculpting on `this.j.Head.bone`**:
   - Hide/replace the old sculpted beards, bald monk dome, sari bun, and blond hair on the legacy head meshes, and attach a **custom-fitted 3D curved facial relief mesh + 3D hair/beard/glasses/topi meshes** directly to `this.j.Head.bone` so the character's face, glasses, beard, and Dhaka Topi animate, nod, turn, and fight seamlessly with the skeleton at 60 FPS.
3. **Bake Clean Outfit & Skin Colors Directly into the GLB Materials**:
   - Strip or replace the old baked diffuse maps on `outfit_top`, `outfit_dhoti`, `outfit_shawl`, `didi_sari`, `didi_blouse`, `trump_body`, `nitin_body`, `Material_0`, and `BakedMaterial` with clean, high-contrast procedural fabric textures matching each Nepali leader's real outfit.

---

## 4. Cache-Busting & Instant Browser Refresh
- Update `server.ts` to send `Cache-Control: no-store, no-cache, must-revalidate` in development so the browser never serves stale `.js`, `.css`, or `.glb` files.
- Add `?v=20261105_samsad3d` cache-busting query strings to `main-CfQ2THv5.js`, `main-C4DN45Lw.css`, `/faces/*.webp`, and `/models/*.glb` in `public/index.html` and `index.html`.
