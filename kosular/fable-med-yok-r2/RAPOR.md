# RAPOR — Molly's Nightstand

Dosya: `sonuc.blend` · Koleksiyon: `Molly's Nightstand` · 12 parça · metre ölçeğinde · malzeme/renk yok.
Üretim: `insa.py` (headless, bmesh ile parametrik). Önizlemeler: `onizle.py` → `onizleme/*.png` (Workbench).

Genel ölçü (modifier'lar uygulanmış): taban 0.40 × 0.40 m (kulplarla derinlik 0.417), boy 0.80 m.

## Parçalar ve modifier'lar

| Parça | Yöntem | Modifier'lar |
|---|---|---|
| `Govde` | Z boyunca 29 halka ile loft edilmiş, köşeleri 3.5 cm yarıçaplı yuvarlatılmış kare kesit. Yarı-genişlik profili: alt 0.14 → göbek 0.185 (gövde yüksekliğinin %58'inde) → üst 0.17; iki parabol, C¹ sürekli. Gövde z 0.07–0.74. | Bevel `Alt_pah` (vertex group `alt`, 6 mm, 3 seg) · Smooth by Angle |
| `Tabla` | Yarı-genişlik 0.20 (göbekten 1.5 cm, üst kenardan 3 cm taşar), köşe yarıçapı 4.5 cm, kalınlık 6 cm (z 0.74–0.80). | Bevel `Ust_yuvarlak` (vgroup `ust`, 24 mm, 12 seg — dolgun üst kenar) · Bevel `Alt_pah` (vgroup `alt`, 7 mm, 1 seg — pah) · Smooth by Angle |
| `Cekmece_Paneli` | Yükseklik 20 cm (z 0.51–0.71). Ön yüzü gövde ön yüzünü izler: her z'de gövde yarı-genişliğinden +8 mm dışarı, −12 mm içeri (gövdeye gömülü sırt). Dış hat da gövdeyle daralır (kenardan 4.5 cm içeride), köşe yarıçapı 2 cm. | Bevel `Yumusak_kenar` (açı, 4.5 mm, 4 seg) · Smooth by Angle |
| `Kapak_Paneli` | Aynı yöntem, 40 cm (z 0.102–0.502). Çekmeceyle arasında 8 mm boşluk. | Bevel `Yumusak_kenar` · Smooth by Angle |
| `Cekmece_Kulp`, `Kapak_Kulp` | Basık topuz: 17 mm yarıçaplı UV küre, derinlik yönünde 0.55 ölçek (Ø34 × 19 mm). Panel merkezinde. | Smooth by Angle |
| `Cekmece_Kulp_Mil`, `Kapak_Kulp_Mil` | Ø11 mm, 26 mm silindir (panele gömülü, 14 mm görünür). | Bevel `Pah` (1.2 mm, 2 seg) · Smooth by Angle |
| `Ayak_1..4` | Kesik koni: üst Ø64 mm, alt Ø50 mm, 7.5 cm boy, merkezleri ±0.095 m (köşelere yakın), gövdeye 5 mm gömülü. | Bevel `Pah` (açı, 6 mm, 4 seg) · Smooth by Angle |

Tüm parçalar smooth gölgeli; 35° üstü kenarlar keskin işaretli, bevel'ler `harden_normals` ile.
"Smooth by Angle" düğüm grubu dosyaya yerel yapıldı (dış kütüphane bağımlılığı yok).

## Yöntem

Profil tabanlı loft seçildi: gövde ve paneller kod ile halka halka üretildiğinden bombe tek bir fonksiyonla
(`body_half(z)`) tanımlı ve paneller bu fonksiyonu aynen kullanarak gövde yüzeyini izliyor. Keskin kenar yok;
kesit köşeleri geometride yuvarlak, yatay kenarlar Bevel modifier'larla (düzenlenebilir kalsın diye uygulanmadı).
Önizlemeler (üç çeyrek, ön, yan, alttan çeyrek, kulp detayı) brief ile karşılaştırıldı; ilk turda sahnede kalan
varsayılan küp temizlendi, ikinci turda şekil onaylandı.

## Brief'in boşta bıraktığı yerler (varsayımlar)

- **Bombe miktarı / konumu:** göbek +1.5 cm (üstten) ve +4.5 cm (alttan) yarı-genişlik farkı, göbek orta-üstte. "Belirgin daralma" alt genişliği 28 cm'e düşürerek yorumlandı.
- **Tabla taşması:** her yandan 1.5 cm (göbeğe göre); kalınlık 6 cm.
- **Panel oranları:** çekmece 20 cm, kapak 40 cm; üst/alt pay 3 cm; aralık 8 mm; taşma 8 mm. Panel dış hattının da gövdeyle daralması benim tercihim (brief yalnızca "bombeyi izleyen" diyor).
- **Kulp ölçüsü:** Ø34 mm basık topuz, 14 mm mil — çocuk mobilyası ölçeği.
- **Ayaklar:** silindirik kesik koni (brief kare/yuvarlak demiyor); 7.5 cm boy, gövde 7 cm'de başlar.
- **Kapak menteşe/çekmece kızağı yok:** paneller gövdeye gömülü dekoratif kabuk; iç boşluk modellenmedi.
- Toy Story referansı görsel olarak teyit edilmedi (görsel yok); "sevimli, çizgi film" hissi dolgun tabla, basık kulp ve belirgin bombe ile verildi.
