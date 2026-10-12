# RAPOR — Molly's Nightstand

Dosya: `sonuc.blend`, koleksiyon `Molly's Nightstand`. Metre ölçeğinde; malzeme/renk yok.
Üretim: `build.py` (headless), önizleme: `render.py` → `preview_*.png` (Workbench).

## Ölçüler
- Taban planı 0.40 × 0.40 m (gövde en şişkin yerinde), tabla 0.43 × 0.43 m, toplam yükseklik 0.80 m.
- Ayak 0.06 m, gövde 0.06 → 0.765 m, tabla 0.035 m kalın.

## Parçalar ve modifier'lar
| Parça | Yöntem | Modifier |
|---|---|---|
| Body | 29 adet yuvarlatılmış-kare halka (bmesh) yükseklik profiline göre ölçeklenip loft edildi. Yarı genişlik: altta 0.17, ~%63 yükseklikte 0.20 (maks), üstte 0.19 (parabolik profil). Köşe yarıçapı 0.05 m, genişlikle orantılı. | Bevel 6 mm, 3 segment, açı sınırı 35° (alt/üst yatay kenarlar) |
| Top | Yuvarlatılmış-kare halkalar loft: altta 5 mm 45° pah, düz yan, üstte 16 mm çeyrek daire (dolgun üst kenar). Plan köşe yarıçapı 0.04. | — (profil mesh'e işli) |
| Drawer Front | Gövde profilini izleyen ince panel (12 dilim); ön yüz gövdeden 8 mm taşar, arka yüz gövdeye 12 mm gömülü. 0.34 × 0.211 m. | Bevel 6 mm, 4 segment, açı 30° |
| Door | Aynı yöntem, 0.34 × 0.421 m (çekmecenin 2 katı). Aralarında 8 mm boşluk. | Bevel 6 mm, 4 segment, açı 30° |
| Drawer Knob / Door Knob | UV küre r=0.022, Y ekseninde 0.55 basık; panel merkezinde. | — |
| … Knob Stem | Silindir r=0.006, 16 mm, panele gömülü kısa mil. | — |
| Foot FL/FR/BL/BR | Kesik koni: üst r=0.031, alt r=0.025, 0.07 m (1 cm gövdeye gömülü). Köşelerden 4.5 cm içeride. | Bevel 4 mm, 3 segment, açı 40° |

Tüm parçalar smooth shading; hiçbir modifier uygulanmadı (uygulanabilir halde).

## Seçilen yöntem
Bombeli gövde için subdivision yerine kontrollü loft seçildi: her yükseklikte yarı genişlik ve köşe
yarıçapı bir fonksiyondan geliyor, bu sayede ön paneller aynı fonksiyonla gövdenin bombesini tam izliyor.
Tablanın üst yuvarlağı ve alt pahı aynı halka-loft yaklaşımıyla profile işlendi (tek Bevel modifier
ile iki farklı kenar profili verilemeyeceği için).

## Tarifin belirsiz bıraktıkları (varsayımlar)
- Bombenin miktarı ve en şişkin noktanın yeri: ±1.5 cm, yüksekliğin ~%63'ü; alt daralma 3 cm (yarı genişlikte).
- Tabla taşması: gövde maksimumundan 1.5 cm, gövde üstünden 2.5 cm.
- Panel kenar boşlukları (3 cm yan, 3–3.5 cm alt/üst), ara boşluk 8 mm, panel taşması 8 mm.
- Topuz boyutu (çap 4.4 cm, derinlik 2.4 cm) ve mil uzunluğu.
- Ayak kalınlığı/daralması ve köşelere uzaklığı; ayakların gövdenin daralan tabanına göre yerleşimi.
- Arka yüz: panel yok, gövde düz (tarif değinmiyor).

## Kontrol
`preview_front34/front/side/low34.png` tarife göre incelendi: bombe, aşağı daralma, dolgun tabla kenarı,
1:2 çekmece/kapak oranı, basık topuzlar ve daralan ayaklar okunuyor. İlk turda topuzlar küçük, ayaklar
ince duruyordu; büyütüldü.
