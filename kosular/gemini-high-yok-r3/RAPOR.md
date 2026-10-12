# RAPOR — Molly's Nightstand

Dosya: `sonuc.blend`  
Tüm parçalar istisnasız `Molly's Nightstand` koleksiyonu içerisindedir.  
Ölçüler gerçek dünya ölçeğinde (metre cinsinden), taban orijini (0, 0, 0) zemin merkezli, mobilyanın ön yüzü −Y yönüne bakacak şekilde kurulmuştur.  
Geometri saftır; hiçbir malzeme, doku veya renk atanmamıştır (`0 materials`).  
Üretici Python betiği: `build_nightstand.py`, görsel kontrol betiği: `render_previews.py`.

---

## 1. Parçalar ve Modifier'lar

Toplam 10 adet bağımsız nesne bulunmaktadır:

| Parça Adı | Açıklama & Boyutlar | Uygulanan Modifier'lar |
|---|---|---|
| `CabinetBody` | Gövde karkası ($Z = 0,095 - 0,755$ m). Bombeli yan profilli: altta 33 cm genişlikten başlayıp %65 yükseklikte 40 cm'ye şişkinleşen ve üstte 38 cm'ye daralan kare planlı gövde. Dikey köşeler $R = 3,5$ cm yuvarlatılmış 33 halkadan loft edildi. | • `Bevel` (Genişlik: 5 mm, 3 segment, Açılı limit $40^\circ$ — gövde alt ve üst kapak kenarlarını yumuşatır)<br>• `WeightedNormal` |
| `TableTop` | Üst tabla ($Z = 0,755 - 0,800$ m, kalınlık 4,5 cm). $43 \times 43$ cm kare plan; gövdeden her yönde 2,5 cm taşar. Üst kenar $R = 20$ mm dolgun çeyrek yuvarlak kordon (bullnose), alt kenar 8 mm $45^\circ$ pahlı (chamfer). Köşeler $R = 40$ mm yuvarlatılmıştır. | • `WeightedNormal` (Form doğrudan quad geometri halkalarıyla modellendiği için pürüzsüz gölgeleme sağlar) |
| `DrawerFront` | Üst çekmece ön paneli ($Z = 0,520 - 0,705$ m, yükseklik 18,5 cm, genişlik 29,6 cm, kalınlık 12 mm). Gövde ön yüzünden 8 mm dışarı taşar, arkası 4 mm gövdeye gömülüdür. Gövdenin düşey bombe profilini birebir takip eder. Basık ve yatay formdadır. | • `Bevel` (Genişlik: 5 mm, 4 segment, Açılı limit $45^\circ$ — panel çevresini yumuşatır)<br>• `WeightedNormal` |
| `DoorFront` | Alt kapak ön paneli ($Z = 0,145 - 0,515$ m, yükseklik 37,0 cm — çekmecenin tam 2 katı; genişlik 29,6 cm). Çekmece ile arasında 5 mm boşluk bulunur. Gövdenin ön bombe eğrisini takip eder ve 8 mm dışarı taşar. | • `Bevel` (Genişlik: 5 mm, 4 segment, Açılı limit $45^\circ$)<br>• `WeightedNormal` |
| `KnobDrawer` | Çekmece kulpu ($Z = 0,6125$ m, çekmecenin tam ortasında). 12 mm uzunluğunda, $\varnothing 13$ mm mil üzerinde, $\varnothing 42$ mm çapında basık yuvarlak topuz (mantar/bun formunda). Panel yüzey normaline dik hizalanmıştır. | • `Subdivision` (Viewport Seviye 1, Render Seviye 2) |
| `KnobDoor` | Kapak kulpu ($Z = 0,330$ m, kapağın tam ortasında). 12 mm boyunda mil üzerinde $\varnothing 42$ mm basık topuz. Panel yüzey normaline dik açılı yerleştirilmiştir. | • `Subdivision` (Viewport Seviye 1, Render Seviye 2) |
| `Leg_FL` | Sol ön ayak (Zemin $Z = 0,000 - 0,100$ m, gövde altına 5 mm geçmeli). Aşağı doğru hafifçe daralan konik ayak ($\varnothing 58$ mm $\rightarrow$ $\varnothing 42$ mm). Zeminle temas eden alt kenarı yuvarlatılmış pabuçlu. Köşeye yakın ($X = -0,122$, $Y = -0,122$). | • `Bevel` (Genişlik: 3 mm, 3 segment, Açılı limit $45^\circ$)<br>• `WeightedNormal` |
| `Leg_FR` | Sağ ön ayak ($X = +0,122$, $Y = -0,122$). Sol ön ayakla aynı formda. | • `Bevel`<br>• `WeightedNormal` |
| `Leg_BL` | Sol arka ayak ($X = -0,122$, $Y = +0,122$). Sol ön ayakla aynı formda. | • `Bevel`<br>• `WeightedNormal` |
| `Leg_BR` | Sağ arka ayak ($X = +0,122$, $Y = +0,122$). Sol ön ayakla aynı formda. | • `Bevel`<br>• `WeightedNormal` |

---

## 2. Seçilen Yöntem

- **Parametrik & BMesh Modelleme:** Tüm parçalar Blender Python API (`bmesh`) kullanılarak matematiksel eğriler ve profiller üzerinden üretildi.
- **Gövde Bombesi:** Gövde genişliği $w(z)$, altta 16,5 cm yarı genişlikten başlayıp $Z \approx 0,52$ m civarında zirveye (20 cm) çıkan ve üstte 19 cm'de biten $C^1$ sürekliliğindeki trigonometrik/spline eğrisiyle loft edildi. Tüm halkalarda dikey köşe yuvarlatmaları 12'şer segmentlik çeyrek yaylarla oluşturularak keskin köşe bırakılmadı.
- **Tabla Profili:** Üst tablanın altındaki 8 mm pah ve üstündeki 20 mm dolgun yuvarlak kenar, 10 kademeli profil halkalarının loft edilmesiyle doğrudan poligon akışına dahil edildi.
- **Panellerin Bombeyi İzlemesi:** Çekmece ve kapak panelleri $16 \times 16$ ve $16 \times 24$ saf quad ızgara olarak üretildi. Ön ve arka yüzey vertex'lerinin derinlik koordinatları gövdenin bombe fonksiyonu $Y(z) = -w(z) - 0,008$ ile hesaplanarak gövde yüzeyiyle kusursuz paralellik sağlandı. Panellerin dikey kenarları mimari ve marangozluk standartlarına uygun olarak düşey eksende düz tutuldu ve aralarındaki boşluk (reveal) temiz bir çizgi olarak korundu.
- **Kulplar:** Kısa mil ve basık küresel topuz formu 24 radyal segmentli devir (lathe) olarak örüldü; yüzeyin yerel eğim açısına göre rotasyon matrisi atanarak panel yüzeyine dik bastırıldı.
- **Yüzey Gölgeleme:** Tüm objelerde `shade_smooth()` aktif edilip düz/kavisli alanların netliği için `WeightedNormal` kullanıldı; kulp gibi organik tornalanmış parçalarda `Subdivision Surface` tercih edildi.

---

## 3. Brifin Yoruma Bıraktığı / Tahmin Edilen Noktalar

1. **"Yaklaşık 40 × 40 cm taban, boyu 80 cm civarı":**
   - Tabla $43 \times 43$ cm (çıkıntılı kenarlar dahil), gövde en geniş yerinde $40 \times 40$ cm, taban genişliği ise $33 \times 33$ cm olarak kurgulandı. Toplam yükseklik tam 80 cm ($0,800$ m) yapıldı.
2. **Bombeli yanlar ve daralma miktarı:**
   - Brifte "ortada biraz şişkin, aşağı doğru belirgin şekilde daralıyor" deniyordu. Üst genişlik 38 cm, orta şişkinlik 40 cm (2 cm hafif bombe), alt taban ise 33 cm (7 cm belirgin daralma) olarak belirlendi.
3. **Çekmece ve Kapak Yükseklikleri ile "Basık" Orantısı:**
   - 1:2 oranı gövde yüksekliğine uygulanırken; çekmece 18,5 cm, alt kapak 37,0 cm olarak ayarlandı. Aralarında 5 mm boşluk bırakıldı. Bu ölçüler üstte 5 cm tabla altı kuşağı, altta 5 cm etek kuşağı bırakarak çekmecenin 29,6 × 18,5 cm ile gerçekten basık (1,6:1 en-boy oranı) görünmesini sağladı.
4. **Kulp Yerleşimi:**
   - Geleneksel dolaplarda kapak kulpu genelde açılma yönüne yakın kenara konur; ancak brifte açıkça *"Her panelin ortasında küçük yuvarlak, basık topuz kulp"* dendiği için her iki kulp da panellerinin geometrik merkezine yerleştirildi.
5. **Ayak Formu ve Konumu:**
   - Brifte "dört kısa, kalın, aşağı doğru hafif daralan ayak; köşelere yakın" denmişti. Ayak yüksekliği 9,5 cm (mobilyanın ~%12'si), üst çapı 5,8 cm (oldukça kalın), alt çapı 4,2 cm seçildi; köşelere sağlam oturması için $X, Y = \pm 12,2$ cm merkezlerine yerleştirildi.
6. **İç Mekanizma:**
   - Brif sadece dış mobilya görünüşünü tarif ettiğinden çekmece kutusu ve dolap içi raflar modellenmedi, panel arkası kapalı bırakıldı.

---

## 4. Önizleme ve Doğrulama Kontrolleri

Workbench render motoruyla `onizleme/` klasörüne çoklu açılardan (perspektif, ön ortografik, yan ortografik, üst plan, kulp ve tabla detayları) yüksek çözünürlüklü önizlemeler alındı.
- Çekmece ve kapak panellerinin bombe takibi kontrol edildi.
- Üst tablanın dolgun kordonu ve alt pahı detay karesinde incelendi.
- Ayakların orantısı ve köşelere yakınlığı teyit edildi.
- `verify_blend.py` ile otomatik geometri, ölçek, malzeme yokluğu ve koleksiyon doğrulaması başarıyla tamamlandı.
