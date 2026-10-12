# Rapor — Molly's Nightstand

Dosya: `sonuc.blend` — koleksiyon `Molly's Nightstand`, 10 parça, malzeme/renk yok.
Üretici betik: `yap.py` (headless; `sonuc.blend`'i yazar, sonra `onizleme/` altına Workbench önizlemeleri basar).
Gerçek ölçek, metre. Genel kutu: 0.44 × 0.44 × 0.80 m (tabla dahil); gövde göbekte 0.40 m, altta 0.325 m, tabla 0.44 m.

## Parçalar ve modifier'lar

| Parça | Geometri | Modifier |
|---|---|---|
| Body | 26 halkalı loft; her halka köşe yarıçapı 42 mm olan yuvarlatılmış kare (8 segment/köşe). Halka genişliği `body_w(z)`: altta 0.325, göbek (yüksekliğin %62'sinde) 0.40, üstte 0.385; iki parabol C¹ birleşir. | Bevel (vertex group `bot`, 12 mm, 3 seg) — alt kenar yumuşatma |
| Top | 0.44 × 0.44 × 0.055 tabla, plan köşe yarıçapı 55 mm (10 seg). | Bevel Top Round (vgroup `top`, 24 mm, 8 seg, profil 0.5) — dolgun yuvarlak üst kenar; Chamfer Bottom (vgroup `bot`, 5 mm, 1 seg) — hafif pah |
| Drawer Front | 260 × 193 mm, köşe yarıçapı 22 mm. Tamamı quad satır ızgarası; dış sütunlar köşe yayını izler. Her vertex kendi yüksekliğindeki gövde ön yüzüne (`-body_w(z)/2`) kaydırılır → panel bombeyi birebir izler. 8 mm dışarı taşar, 12 mm gövdeye gömülü. | Bevel (açı 40°, 5.5 mm, 3 seg) — yumuşak kenarlar |
| Door | 260 × 385 mm, aynı yöntem; çekmecenin ~2 katı. Aralık 12 mm. | Bevel (açı, 5.5 mm, 3 seg) |
| Knob Drawer / Knob Door | Ø13 mm, 12 mm mil + Y'de 0.6 basılmış Ø38 mm küre; panel merkezinde, panel ön yüzüne oturur. | — |
| Leg FL/FR/BL/BR | Konik silindir: üst r 32 mm, alt r 23 mm, boy 102 mm (12 mm gövdeye girer). Merkezler ±115 mm (köşelere yakın, gövde alt köşe yayının içinde). | Bevel (açı, 7 mm, 3 seg) — ayak ucu yuvarlatma |

Tüm yüzeyler smooth; bevel'lerde harden normals açık. Modifier'lar uygulanmamış (düzenlenebilir).

## Yöntem

Çizim olmadığı için her parça bmesh ile parametrik üretildi; tek kaynak `yap.py` içindeki ölçü sabitleri.
Gövdenin bombe profili tek bir `body_w(z)` fonksiyonunda toplandı; paneller ve kulplar aynı fonksiyonu kullandığı için gövdeyi değiştirince önü de birlikte değişir.
Paneller ilk denemede n-gon şeritlerle (bisect) yapıldı; eğrilik sonrası düzlemsel olmayan n-gon'lar tessellation'da siyah şerit verdi; tamamen quad ızgaraya çevrildi, sorun kalktı.

## Kontrol

`onizleme/34.png`, `front.png`, `side.png`, `low34.png`, `close.png` — Workbench, studio ışık, cavity.
Brief maddeleri tek tek bakıldı: kare plan, 80 cm boy, göbekli ve aşağı daralan gövde, yumuşak dikey köşeler, taşan kalın tabla (yuvarlak üst / pahlı alt / yuvarlak köşe), basık çekmece + iki kat kapak, bombeyi izleyen taşkın paneller, ince aralık, basık topuz kulplar, köşelere yakın konik ayaklar — hepsi var.

## Tahmin edilen (brief'te belirsiz) noktalar

- Taban "~40 cm": göbek genişliği 40 cm, tabla 44 cm alındı (tabla "biraz taşan" olduğu için).
- Göbeğin yeri ve miktarı: üst-ortada (%62), alta doğru 7.5 cm daralma — "belirgin" diye yorumlandı.
- Ayak yüksekliği 9 cm, yuvarlak kesit (brief kesit söylemiyor; çizgi film havasına yuvarlak uygun göründü).
- Panel taşması 8 mm, aralık 12 mm, panel genişliği 26 cm (gövde alt genişliğinin düz kısmına sığacak şekilde).
- Tabla kalınlığı 5.5 cm, kulp çapı 3.8 cm.
- Çekmece/kapak arası boşluk gövdeyi kesmiyor; çekmece ve kapak açılmaz (içi boş değil), yalnızca ön paneller.
