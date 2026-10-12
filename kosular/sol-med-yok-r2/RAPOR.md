---
yazan: codex
model: gpt-6
---

# Molly's Nightstand

**Olgu — kaynak:** `tarif.md` sözlü tasarım tarifi; `GOREV.md` teslim ve çalışma koşulları. Model metre ölçeğinde, yalnızca headless Blender ile üretildi. `sonuc.blend` içindeki 12 mesh parçanın tamamı `Molly's Nightstand` koleksiyonundadır. Malzeme, doku veya nesne rengi atanmamıştır; önizlemelerde Workbench'in ortak nötr görüntüleme rengi kullanıldı.

| Parça | Yöntem | Modifier |
|---|---|---|
| Gövde (1) | Yuvarlatılmış kare kesitlerin yükseklik boyunca loft'u; orta bombe, daralan alt, 15 mm duvarlı kapalı kabuk | Bevel 4 mm / 4 segment; Weighted Normal |
| Tabla (1) | Yuvarlatılmış kare kesitler; alt pah ve üstte 18 mm yarıçaplı dolgun kenar doğrudan profil geometrisi | Bevel 1,2 mm / 3 segment; Weighted Normal |
| Çekmece ve kapak paneli (2) | Gövde derinlik ve genişlik eğrisine uyarlanmış, kapalı, 10 mm kalınlığında yüzeyler | Bevel 3,5 mm / 4 segment; Weighted Normal |
| Kulp milleri (2) | Kısa silindir | Bevel 1,5 mm / 3 segment; Weighted Normal |
| Kulp başları (2) | Derinliği basık UV küre | Yok; smooth shading |
| Ayaklar (4) | Yuvarlatılmış kare kesitli, aşağı daralan loft | Bevel 5 mm / 4 segment; Weighted Normal |

**Varsayım / tasarım yorumu:** 40 × 40 cm nominal taban ölçüsü tabla planı olarak alındı. Tabla kalınlığı 6,5 cm; toplam yükseklik 80 cm. Gövde tabanda 30,2 cm, üstte 34,6 cm, ortada yaklaşık 36,4 cm genişliktedir. Kulp dahil dış sınır 40 × 42,18 × 80 cm'dir. Ayakların görünen yüksekliği yaklaşık 8,5 cm; üst kesiti 5,8 cm, alt kesiti 4,7 cm. Kapak 33,6 cm, çekmece 16,8 cm yüksekliğinde; oran tam 2:1, aradaki boşluk 8 mm. Kulp çapı 34 mm. Bu ayrıntı ölçüleri tarifte verilmediği için yorumlandı.

**Kapsam:** Tarifin dış görünüşü modellendi. Çekmece kutusu, ray, menteşe ve açılma mekanizması tarif edilmediği için eklenmedi; ön paneller sabittir. Görsel referans verilmediğinden filmdeki nesnenin birebir kopyası olduğu iddia edilmez.

**Doğrulama:** `on_capraz.png`, `on.png`, `yan.png` üretilip tarifle görsel olarak karşılaştırıldı. İlk önizlemedeki uzun ayaklar kısaltılıp kalınlaştırıldı. Son çapraz görünüş tekrar incelendi. Modifier uygulanmış geometri kontrolü: 12 parça, sıfır manifold olmayan kenar, sıfır atanmış malzeme. Ölçü ve parça verileri `kontrol.json` içinde; yeniden üretim betiği `model.py`.
