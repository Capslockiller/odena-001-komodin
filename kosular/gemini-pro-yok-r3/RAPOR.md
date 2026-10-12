# Molly's Nightstand - Model Raporu

## Parçalar ve Kullanılan Değiştiriciler (Modifiers)

Model `Molly's Nightstand` adlı koleksiyonda organize edilmiştir. Aşağıdaki parçalardan oluşmaktadır:

* **Body (Gövde):**
  * `Bevel`: Dikey köşelerin yumuşak hatlara sahip olması için açı tabanlı kullanıldı.
  * `Lattice (Bulge)`: Ortadan şişip alta doğru daralma efektini sağlamak için.
* **TopBoard (Üst Tabla):**
  * (Modifier kullanılmadı). Blender versiyonları arası olası ağırlık (bevel weight) hatalarını önlemek için üst tablanın kenarları ve köşeleri `BMesh` üzerinden "destructive" (kalıcı) bevel işlemi ile modellendi. Üst kenar tam ve dolgun, alt kenar hafif pahlı, köşeler ise yuvarlatılmış olarak işlendi.
* **Drawer (Çekmece) ve Door (Kapak):**
  * `Bevel`: Kenarların keskinliğini almak için açı tabanlı.
  * `Lattice (Bulge)`: Gövdenin bombesini pürüzsüzce takip etmeleri için eklendi.
* **Knob_Drawer ve Knob_Door (Kulplar):**
  * `Lattice (Bulge)`: Panellerle birlikte hizalı deforme olmaları için.
* **Leg_0_0, Leg_0_1, vs. (Ayaklar):**
  * `Bevel`: Yere basan alt kenarların hafif yumuşatılması için.
* **Body_Lattice (Kafes):**
  * Gövdeyi, çekmece/kapağı ve kulpları aynı anda deforme ederek şişkinlik ve daralma formunu (cartoon hissini) veren ana kontrol nesnesi.

## Seçilen Yöntem

Model oluşturulurken tamamen Python script kullanıldı (`build.py`). Çizgi film (cartoon) hissiyatı veren organik "ortası şişkin, altı dar" formu vermek için **Lattice Modifier** yöntemi seçildi. Gövde ve panellerin (çekmece/kapak) mesh yapıları, Lattice ile pürüzsüzce bükülebilmesi için yeterince alt bölümlere (subdivide) ayrıldı. Bu sayede paneller gövde bombesini mükemmel bir şekilde takip etti. Bütün nesnelere Smooth Shading uygulandı.

## Tahmin Yürütülen Kısımlar (Brief'te Açık Bırakılanlar)

1. **Ölçü Dağılımı:** Yaklaşık 40x40 cm taban ve 80 cm boy denildiği için; bacakları 10 cm, üst tablayı 5 cm, gövdeyi ise 65 cm yüksekliğinde varsaydım. Tabla gövdeden taştığı için gövde genişliğini 36x36 cm civarında başlattım.
2. **Kapak Kulpunun Yeri:** "Her panelin ortasında" dendiği için alttaki kapağın da kulpunu tam merkeze yerleştirdim. Yana açılan kapaklarda kulp genelde kenarda olur, ancak çizgi film mobilyalarında veya aşağı/yukarı açılan kapaklarda simetri daha yaygındır.
3. **Ayakların Bağlantısı:** Gövdenin aşağı doğru daralması nedeniyle, bacakların da bu daralmış olan alt taban genişliğine sığacak şekilde köşelere yakın ve içe dönük yerleştirilmesi gerekti, bunu Lattice deformasyonu ile uyumlu olacak oranlarda varsaydım.
