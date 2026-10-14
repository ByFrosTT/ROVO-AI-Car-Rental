// ROVO remote image mapping — verified real-car image URLs from web image results
// For production, download these images locally instead of hotlinking third-party servers.
const CAR_IMAGES_REMOTE = {
  "Maruti Suzuki Swift": "https://content.carlelo.com/uploads/variant-option/cq2cGOSXpF7Ck6ZDzqi2xay1wh9ZnJcpa0OWEAcd.webp", // CarLelo
  "Maruti Suzuki Baleno": "https://imgd.aeplcdn.com/1280x720/n/cw/ec/102663/baleno-exterior-right-front-three-quarter-69.jpeg?isig=0&q=80", // CarWale
  "Maruti Suzuki Fronx": "https://img.autocarindia.com/model/uploads/modelimages/Maruti-Suzuki-Fronx-130120231644.jpg", // Autocar India
  "Maruti Suzuki Brezza": "https://asset.autocarindia.com/static/car-images/maruti-suzuki_brezza.png?fm=auto&q=75&w=728", // Autocar India
  "Maruti Suzuki Grand Vitara": "https://cdn1.smartprix.com/rx-iMQa67SjM-w1200-h1200/MQa67SjM.webp", // Smartprix
  "Maruti Suzuki Ertiga": "https://static.caronphone.com/public/brands/21/70/903/903_1708949321.webp", // CarOnPhone
  "Maruti Suzuki XL6": "https://d91ztqmtx7u1k.cloudfront.net/ClientContent/Images/Catalogue/premium-silvernexa-blue-marut-20240513154646149.jpg", // Aajjo
  "Hyundai Grand i10 Nios": "https://static-cdn.cars24.com/prod/auto-news24-cms/Cars24-Blog-Images/2024/11/26/ffe1f023-9230-42f3-9793-565b283dfbfd-Nios-%28Compressify.io%29.jpg", // CARS24
  "Hyundai i20": "https://cdni.autocarindia.com/ExtraImages/20250519031920_2025_Hyundai_i20_prices.jpg?q=75&w=640", // Autocar India
  "Hyundai Aura": "https://media.zigcdn.com/media/model/2026/Feb/front-1-4-left-1812283041_930x620.jpg", // ZigWheels
  "Hyundai Verna": "https://www.motornet.com.br/files/uploads/1d3d7407-46a8-4cd8-96c0-8ce24bdc254b.jpg", // MotorNet
  "Hyundai Venue": "https://images.carexpert.com.au/resize/3000/-/app/uploads/2023/01/2023-hyundai-venue-colours-3.png", // CarExpert
  "Hyundai Creta": "https://hyundai.petroautos.com/assets/uploads/161471729940295.png", // Hyundai Petroautos
  "Hyundai Alcazar": "https://img.autocarpro.in/autocarpro/Portals/0/userfiles/17/9_1.jpg", // Autocar Professional
  "Hyundai Ioniq 5": "https://www.topgear.com/sites/default/files/2022/01/3.%20hyundai-ioniq-5-uk-exterior-01.jpg?h=930&w=1654", // Top Gear
  "Tata Tiago": "https://1.bp.blogspot.com/-sQM3QZDk2b0/Vx-68d9eWUI/AAAAAAAAB4Y/VJQQ9hmmo-47_Y5BGrQr5Cb6TNP3QJpvwCLcB/s1600/Tata-Zica-Gallery-7.png", // Automobile Planet
  "Tata Tiago EV": "https://img.autocarindia.com/mmv_images/colors/20250516045323_Tata_Tiago_EV_Teal_Blue%5B1%5D.png?c=1&h=500&q=90&w=750", // Autocar India
  "Tata Altroz": "https://static-cdn.cars24.com/prod/new-car-cms/Tata/Altroz-2025/2025/05/22/7d307c1f-e37d-43ac-b7d9-ed04a8790be3-PrestineWhite-0-1.png?dpr=3&format=auto&optimize=low&quality=50&w=400", // CARS24
  "Tata Tigor": "https://asset.autocarindia.com/static/car-images/tata_tigor.png", // Autocar India
  "Tata Tigor EV": "https://cdni.autocarindia.com/Utils/ImageResizer.ashx?c=1&h=795&n=https%3A%2F%2Fcdni.autocarindia.com%2FExtraImages%2F20210831105957_Tata+Tigor+1.jpg&w=1200", // Autocar India
  "Tata Punch": "https://imgd-ct.aeplcdn.com/1056x660/n/8ae844a_1535735.jpg?q=75", // CarTrade
  "Tata Punch EV": "https://car.zigcdn.com/images/car-images/930x620/Tata/Punch-EV/13330/1771576353683/223_Pure-Grey_cecfd1.jpg", // ZigWheels
  "Tata Nexon": "https://imgd.aeplcdn.com/1056x594/n/t6e05sa_1478705.jpg?q=75&wm=1", // CarWale
  "Tata Nexon EV": "https://ik.imagekit.io/yktechnology/cars/tata/nexon-ev/gallery/nexon-ev-1.webp?tr=w-3840", // CarVCar
  "Tata Harrier": "https://fcache1.pakwheels.com/original/4X/b/4/3/b43aca6e7464519437a3b63c9a13fd827fc9ae94.jpg", // PakWheels
  "Tata Safari": "https://cdni.autocarindia.com/ExtraImages/20210131124626_Tata_Safari_tracking_front.jpg", // Autocar India
  "Mahindra XUV 3XO": "https://stimg.cardekho.com/images/carexteriorimages/630x420/Mahindra/XUV-3XO/10184/1758199247932/front-left-side-47.jpg?tr=w-664", // CarDekho
  "Mahindra XUV700": "https://cdn.zeebiz.com/sites/default/files/2024/05/22/294945-xuv.jpg", // Zee Business
  "Mahindra Scorpio N": "https://www.agnigroup.com.np/templates/yootheme/cache/18/scorpion-intro-18e4dcb8.png", // Agni Group
  "Mahindra Thar": "https://akm-img-a-in.tosshub.com/indiatoday/images/story/202008/Mahindra_Thar.jpeg?b3fpzLGNWSVmIQ7puqqf_v8naxGtjna5=&size=770%3A433", // India Today
  "Mahindra Thar Roxx": "https://cdn.sanity.io/images/rua5dofm/reviews/95320c7d43e9ec77f8e7c98b99ce37c940f2192c-700x464.webp?fit=max&h=800&q=85&rect=2%2C0%2C696%2C464&w=1200", // CarSauce
  "Mahindra BE 6": "https://content.carlelo.com/uploads/variant-option/everest-white-satin-be-6.webp", // CarLelo
  "Mahindra XEV 9e": "https://img.autocarindia.com/News/Mahindra-XEV-9e-Pack-One.jpg?c=0&w=700", // Autocar India
  "Toyota Glanza": "https://fortune-toyota.com/wp-content/uploads/2025/03/glanza.jpg", // Fortune Toyota
  "Toyota Rumion": "https://car.zigcdn.com/images/car-images/930x620/Toyota/Rumion/8650/1692767042630/221_spunky-blue_283157.jpg", // ZigWheels
  "Toyota Urban Cruiser Hyryder": "https://img.autocarpro.in/autocarpro/234df001-0f6d-4d3b-9871-c4cbe9237567_new-web-Toyota-Urban-Cruiser-Hyryder.jpg", // Autocar Professional
  "Toyota Innova Crysta": "https://stimg.cardekho.com/images/carexteriorimages/930x620/Toyota/Innova-Crysta/9608/1755846139274/front-left-side-47.jpg?impolicy=resize&imwidth=890", // CarDekho
  "Toyota Innova Hycross": "https://static.caronphone.com/public/brands/33/127/836/836_1709020413.webp", // CarOnPhone
  "Toyota Fortuner": "https://www.bakkieandoutdoor.co.za/cdn/shop/collections/2021-2023_GD6_1st_FL_3bd7c5ba-d390-4642-b176-12dbb5acf1ed.png?v=1691833547&width=1500", // Bakkie & Outdoor
  "Kia Sonet": "https://media.newindianexpress.com/newindianexpress/2024-10-26/6xpf3n9b/article.png?auto=format%2Ccompress&enlarge=true&fit=max&h=675&w=1200", // New Indian Express
  "Kia Seltos": "https://images.carexpert.com.au/resize/3000/-/app/uploads/2022/11/2023-Kia-Seltos-1.jpg", // CarExpert
  "Kia Carens": "https://cdn-s3.autocarindia.com/legacy/cdni/Galleries/20211216125004_Carens_1.jpg?q=75&w=640", // Autocar India
  "Kia EV6": "https://editorial.pxcrush.net/carsales/general/editorial/kia-ev6-studio-01.jpg?height=682&width=1024", // Carsales
  "Honda Amaze": "https://mc.bajajfinserv.in/media/catalog/product/h/o/hondaamazevxpetrolmtplatinumwhitepearl_additional2.jpeg", // Bajaj Finserv
  "Honda City": "https://bingolsurmansetcom.teimg.com/bingolsurmanset-com/uploads/2024/09/i-m-g-2381.jpeg", // Bingol Surmanset
  "Honda City e:HEV": "https://stimg.cardekho.com/images/cms/carnewsimages/editorimages/64005cf89e762.jpg", // CarDekho
  "Honda Elevate": "https://akm-img-a-in.tosshub.com/sites/visualstory/wp/2023/06/Front-scaled.jpg", // Business Today
  "Skoda Kylaq": "https://cdni.autocarindia.com/ExtraImages/20250728020708__AAB2101_1_.jpg", // Autocar India
  "Skoda Kushaq": "https://static-cdn.cars24.com/prod/new-car-cms/Skoda_Kushaq_exterior_5_e919b17c9a.jpg", // CARS24
  "Skoda Slavia": "https://imgd.aeplcdn.com/1200x900/n/cw/ec/107629/skoda-slavia-right-front-three-quarter0.jpeg?isig=0&wm=0", // CarWale
  "Volkswagen Virtus": "https://img.autocarpro.in/autocarpro/56d4a726-6867-4741-939c-18c2f878138b_Virtus-.png?c=1&h=490&q=75&w=750", // Autocar Professional
  "Volkswagen Taigun": "https://img.autocarindia.com/ExtraImages/20210331090846_2021_volkswagen_Taigun_front.jpg", // Autocar India
  "MG Comet EV": "https://static.caronphone.com/public/brands/25/465/1853/1853.webp", // CarOnPhone
  "MG Windsor EV": "https://c.ndtvimg.com/2025-07/djdjaqr8_mg-windsor-ev-price-hiked-in-india_625x300_28_July_25.jpg?im=FitAndFill%2Calgorithm%3Ddnn%2Cwidth%3D1200%2Cheight%3D800", // NDTV Auto
  "MG Astor": "https://img.autocarindia.com/Galleries/20210915123202_MG_Astor_front_2.jpg?w=640", // Autocar India
  "MG Hector": "https://img.autocarindia.com/Features/MG-Hector-ADV-1.jpg", // Autocar India
  "MG ZS EV": "https://p.globalsources.com/IMAGES/PDT/B5817082327/electric-cars-electric-vehicles.jpg", // Global Sources
  "Renault Kwid": "https://media.zigcdn.com/media/content/2019/Jun/zw-renault-kwid-1.jpg", // ZigWheels
  "Renault Kiger": "https://www.largus.fr/images/styles/max_1300x1300/public/images/renault-kiger-showcar-2021-7_1.jpg?itok=pImIrbm9", // L'Argus
  "Nissan Magnite": "https://img.autocarpro.in/autocarpro/d9a0e982-3660-4c6f-8493-85ad143cb2bc.jpg?c=1&h=490&q=75&w=750", // Autocar Professional
  "Citroen C3": "https://carlifemotors.com/media/2025/10/%CE%91%CE%BD%CF%8E%CE%BD%CF%85%CE%BC%CE%BF-%CF%83%CF%87%CE%AD%CE%B4%CE%B9%CE%BF-98-660x471.png", // Carlife Motors
  "Citroen Basalt": "https://static.wixstatic.com/media/3d5fff_47911395f7f545719d1a8b0330bac739~mv2.jpg/v1/fill/w_984%2Ch_656%2Cal_c%2Cq_85/3d5fff_47911395f7f545719d1a8b0330bac739~mv2.jpg", // Passionnement Citroen
  "Jeep Compass": "https://cdn-s3.autocarindia.com/legacy/cdni/ExtraImages/20200722105511_Jeep-Compass-diesel-automatic-front.jpg", // Autocar India
  "Jeep Meridian": "https://static.punjabkesari.in/multimedia/18_03_166421358jeep.jpg", // Punjab Kesari
  "BYD Atto 3": "https://www.electrive.com/media/2024/10/byd-atto-3-2024-03-min.jpg", // electrive
  "BYD Seal": "https://storage.mfn.se/0ed03f73-eec8-4760-8cad-75dc0cf1c934/byd-seal-exterior-3.jpeg", // MFN
  "BYD eMAX 7": "https://static-cdn.cars24.com/prod/new-car-cms/BYD/E-max7/2024/10/08/94064cbe-553a-4253-b8b7-57ab71ae9ac4-3-_18_.png?dpr=3&format=auto&optimize=low&quality=50&w=296", // CARS24
  "BMW 2 Series": "https://mediapool.bmwgroup.com/cache/P9/202507/P90610969/P90610969-the-new-bmw-2-series-gran-coupe-alpine-white-driving-07-2025-2200px.jpg", // BMW Group Press
  "BMW 3 Series": "https://www.evanshalshaw.com/-/media/evanshalshaw/blog/best-used-cars-for-motorway-driving/bmw-3-series-driving-1280x720px.ashx", // Evans Halshaw
  "BMW X1": "https://ucalfilo.com/tema/genel/uploads/araclar/ucal-kiralama-bmw-x1-0-1.jpg", // Ucal Filo
  "BMW iX1": "https://www.bmwgroup-werke.com/regensburg/en/_jcr_content/main/layoutcontainer_4_co/slider/sliderparsys/slidercolumnscontain/columncontrolparsys/image.coreimg.jpeg/1760354014727/produkte-teaser-ix1-1280x854.jpeg", // BMW Group
  "Mercedes-Benz A-Class": "https://parkers-images.bauersecure.com/wp-images/213/static-exterior/852x624/082-mercedes-a-class-yellow-static-front.jpg?mode=max&quality=90&scale=down", // Parkers
  "Mercedes-Benz C-Class": "https://www.enterprise.fi/images/enterprise-hp-minilease2.jpg", // Enterprise
  "Mercedes-Benz GLA": "https://www.autocar.co.uk/sites/autocar.co.uk/files/images/car-reviews/first-drives/legacy/1-mercedes-benz-gla-2020-fd-hero-front.jpg", // Autocar UK
  "Audi A4": "https://cdn-s3.autocarindia.com/legacy/cdni/mmv_images/colors/20250527015829_Audi_A4_Glacier_White_Metallic%5B1%5D.png?q=75&w=728", // Autocar India
  "Audi Q3": "https://images.autoweek.nl/261034388/width/800/261034388", // AutoWeek
  "Volvo XC40 Recharge": "https://i.blogs.es/bf04c3/259192_volvo_xc40_recharge_p8_awd_in_glacier_silver/1366_2000.jpg", // Xataka
  "Mini Cooper S": "https://carwow-uk.imgix.net/prismic/b79b3cb5-cc61-4ade-8f4c-e3992b531206_P90302744_highRes_mini-3-door-hatch-in.jpg?auto=format&cs=tinysrgb&fit=clip&ixlib=rb-1.1.0&q=60&w=1920", // Carwow
};