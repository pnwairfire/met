import datetime

HOURLY_PROFILES_HOUR_0 = {
    'HPBL': 100.0,
    'HGTS': [59.20695352193937, 135.82881398535508, 230.2522349481686, 360.414411605392, 518.8055921541387, 715.7651461641137, 962.7815105469939, 1301.743826670549, 1732.0963974479655, 2192.250857281424, 2663.856567251226, 3345.982389068354, 4259.947450680663, 5186.011915491956, 6120.21175643276, 7056.643626913428, 8006.417923710241, 8986.451540456597, 9972.250805846712, 10981.449306410641, 12042.198782182653, 13124.193667771762, 14261.080058165118, 15406.309765306385, 16658.518561184595, 17976.158502586513, 19355.563010823662, 20904.261267868987, 22702.76242092459, 24927.524263410254, 28825.25346629527],
    'PBLH': 0.0,
    'PRES': [993.0,984.0,975.0,961.0,943.0,922.0,896.0,862.0,820.0,778.0,736.0,678.0,608.0,544.0,486.0,432.0,383.0,339.0,299.0,263.0,230.0,200.0,174.0,150.0,130.0,112.0,96.9,83.6,72.3,62.4,53.9],
    'PRSS': 996.0,
    # fixed RELH calculation - it was off by a factor of 10 due to units
    #'RELH': [113.52118179569345, 115.07020100907351, 123.0476250403563, 118.30288856444385, 121.98572106270176, 133.76778670367295, 148.75653839851014, 181.90425174546766, 110.97738136160952, 21.490567359845436, 36.875009044515586, 40.97991571189952, 55.011821182593366, 221.53352322840786, 179.07326909419453, 444.9955979290613, 436.51125329612876, 613.0803545775004, 542.5612363701279, 409.0915794838193, 328.2356599163898, 183.5607632538291, 129.89359101516095, 43.10737045816838, 39.16865264033064, 37.757751935123075, 34.763505573192106, 8.291881754877862, 1.9054685441623844, 1.0641610896592033, 0.6095337384388296]
    'RELH': [11.352118179569345,11.507020100907351,12.30476250403563,11.830288856444385,12.198572106270176,13.376778670367295,14.875653839851014,18.190425174546766,11.097738136160952,2.1490567359845436,3.6875009044515586,4.097991571189952,5.5011821182593366,22.153352322840786,17.907326909419453,44.49955979290613,43.651125329612876,61.30803545775004,54.25612363701279,40.90915794838193,32.82356599163898,18.35607632538291,12.989359101516095,4.310737045816838,3.916865264033064,3.7757751935123075,3.4763505573192106,0.8291881754877862,0.19054685441623844,0.10641610896592033,0.06095337384388296],
    'RH2M': None,
    'SHGT': 112.0,
    'SPHU': [3.2,3.0,2.8,2.5,2.4,2.4,2.4,2.5,1.3,0.24,0.37,0.33,0.31,0.85,0.45,0.75,0.5,0.46,0.26,0.11,0.05,0.02,0.02,0.01,0.01,0.01,0.01,0.003,0.001,0.001,0.002],
    'T02M': 31.5,
    'TEMP': [31.0,29.5,27.0,25.5,24.0,22.1,19.9,16.7,13.4,11.8,9.3,4.8,-1.9,-8.7,-15.7,-22.1,-28.1,-34.3,-40.5,-47.7,-54.5,-59.0,-57.7,-55.9,-57.1,-59.0,-60.7,-61.6,-62.0,-61.9,-61.3],
    'TO2M': None,
    'TPOT': [304.8,304.0,302.3,302.1,302.1,302.2,302.3,302.5,303.3,306.2,308.3,310.6,312.7,314.8,316.5,319.3,322.5,325.6,328.7,330.5,333.0,339.1,355.4,373.6,387.4,400.4,414.3,430.2,447.6,466.9,488.2],
    'TPP3': None,
    'TPP6': None,
    'TPPA': 0.0,
    'U10M': 2.6,
    'UWND': [2.5,2.5,2.3,2.4,2.5,2.6,2.6,2.3,0.75,-2.1,-2.3,-1.2,2.7,6.5,6.3,8.8,11.8,16.4,19.0,17.5,15.4,16.2,19.8,19.6,15.9,11.6,7.6,3.8,0.2,-2.8,-5.3],
    'V10M': -1.8,
    'VWND': [-1.9,-1.8,-1.7,-1.7,-1.7,-1.4,-0.8,-0.1,1.5,4.5,3.8,3.1,4.9,7.8,10.6,13.1,13.7,14.5,17.7,20.1,19.5,18.3,17.5,15.6,13.3,10.6,8.9,9.1,9.2,7.6,5.1],
    'WDIR': [-307.1,305.4,307.2,305.5,304.0,299.0,287.6,272.7,206.4,155.5,149.6,158.9,209.2,219.8,211.1,214.0,221.0,228.9,227.4,221.4,218.6,221.9,228.8,231.8,230.4,228.0,221.1,202.8,181.5,160.3,134.4],
    'WSPD': [3.1,3.1,2.9,3.0,3.0,2.9,2.7,2.3,1.7,5.0,4.4,3.4,5.7,10.2,12.3,15.8,18.1,21.9,26.0,26.6,24.8,24.4,26.4,25.1,20.7,15.7,11.7,9.8,9.2,8.1,7.3],
    'WWND': [-7.0,-7.0,-7.0,-7.0,-3.5,-5.3,-5.3,-3.5,-3.5,-3.5,-2.6,-1.8,-1.3,-0.88,-0.66,-0.44,-0.33,-0.22,-0.11,-0.11,-0.1,-0.03,-0.02,-0.01,-0.01,-0.003,-0.002,-0.0004,-0.0002,-3e-05,0.0],
    # Fix in RELH calculation changed dew_point calculations
    #'dew_point': [33.21869307923373,31.933426648507066,30.549514804568673,28.34132324491975,27.3314691246797,26.939560623783223,26.446202617151414,26.45467475406241,15.01465433571667,-9.855673746450748,-4.890633166932844,-7.562573501077679,-9.910621609646341,2.171643685260335,-8.240899895145844,-3.1006721338965235,-10.281164967906477,-13.163389242763628,-21.94892987537702,-33.40845564121429,-43.288529626885236,-53.641638351327316,-55.39716723768163,-63.10622724045183,-65.01001633093503,-67.06671699877663,-69.28786256539487,-80.62964149370242,-90.63939879384043,-94.13712681828451,-96.42570734383574],
    'dew_point': [-2.6110043729268, -3.613589201269974, -4.69422550297827, -6.420876907421132, -7.211485363941563, -7.518472805734461, -7.905058134600324, -7.8984183067692015, -16.90368872898358, -36.75709441061073, -32.763026654858635, -34.91052410826424, -36.801382771693056, -27.108284348158378, -35.45641916245404, -31.326882687424245, -37.10009268087637, -39.42650955989245, -46.55014474202659, -55.91570028730223, -64.0582365042134, -72.6588478413272, -74.12419778849639, -80.583154334163, -82.18431173882925, -83.91679543932989, -85.79098402077531, -96.63446221386013, -96.91295483061481, -96.84331529836118, -96.42570734383574],
    'lat': 37,
    'lng': -122,
    'pressure': [993.0,984.0,973.0,958.0,940.0,918.0,891.0,855.0,811.0,766.0,722.0,662.0,588.0,520.0,458.0,402.0,351.0,304.0,262.0,224.0,189.0,158.0,130.0,106.0,84.0,65.0,49.0,35.0,23.0,13.0,4.0],
    'pressure_at_surface': 0.0
}
HOURLY_PROFILES_HOUR_1 = {
    'HPBL': 100.0,
    'HGTS': [59.20695352193937,135.82881398535508,230.2522349481686,360.414411605392,518.8055921541387,715.7651461641137,962.7815105469939,1301.743826670549,1742.0947221259023,2192.250857281424,2663.856567251226,3345.982389068354,4259.947450680663,5186.011915491956,6120.21175643276,7056.643626913428,8006.417923710241,8986.451540456597,9972.250805846712,10981.449306410641,12042.198782182653,13124.193667771762,14261.080058165118,15406.309765306385,16658.518561184595,17976.158502586513,19355.563010823662,20904.261267868987,22702.76242092459,24927.524263410254,28825.25346629527],
    'PBLH': 1474.0,
    'PRES': [993.0,984.0,975.0,961.0,943.0,921.0,896.0,862.0,820.0,778.0,736.0,678.0,608.0,544.0,486.0,432.0,383.0,339.0,299.0,263.0,230.0,200.0,174.0,150.0,130.0,112.0,96.9,83.6,72.3,62.4,53.9],
    'PRSS': 996.0,
    # fixed RELH calculation - it was off by a factor of 10 due to units
    #'RELH': [102.42075497187231,106.99940990055696,112.24258342641438,119.40509763179595,127.44170793758467,141.4049403631028,158.17153241270634,172.41920451559116,117.8221251652514,22.976815664117215,37.367340478710304,39.73810008426621,63.884695566882606,198.07703253363522,202.9497049734205,433.129048650953,444.3669459518837,580.9522520945848,505.80371957351826,451.0069790278619,313.8900183643308,161.5561808735467,122.63477535700021,42.14179258569039,38.72240258748246,38.65007617648791,18.44583359473801,8.910414657759606,2.048166503103062,1.1165462712957732,0.6242571740000024],
    'RELH': [10.242075497187231,10.699940990055696,11.224258342641438,11.940509763179595,12.744170793758467,14.14049403631028,15.817153241270634,17.241920451559116,11.78221251652514,2.2976815664117215,3.7367340478710304,3.973810008426621,6.3884695566882606,19.807703253363522,20.29497049734205,43.3129048650953,44.43669459518837,58.09522520945848,50.580371957351826,45.10069790278619,31.38900183643308,16.15561808735467,12.263477535700021,4.214179258569039,3.872240258748246,3.865007617648791,1.844583359473801,0.8910414657759606,0.2048166503103062,0.11165462712957732,0.06242571740000024],
    'RH2M': None,
    'SHGT': 112.0,
    'SPHU': [2.6,2.6,2.6,2.6,2.6,2.6,2.6,2.4,1.4,0.26,0.38,0.32,0.36,0.76,0.51,0.73,0.5,0.44,0.24,0.12,0.05,0.02,0.02,0.01,0.01,0.01,0.005,0.003,0.001,0.001,0.002],
    'T02M': 30.2,
    'TEMP': [29.2,28.3,27.3,26.0,24.6,22.5,20.2,16.9,13.6,12.0,9.5,4.8,-1.9,-8.7,-15.7,-22.1,-28.3,-34.2,-40.6,-47.8,-54.1,-57.9,-57.2,-55.7,-57.0,-59.2,-61.2,-62.2,-62.6,-62.3,-61.5],
    'TO2M': None,
    'TPOT': [303.0,302.8,302.7,302.6,302.8,302.7,302.7,302.7,303.6,306.4,308.5,310.6,312.7,314.8,316.5,319.2,322.2,325.5,328.5,330.4,333.6,341.0,356.2,373.9,387.5,400.1,413.3,429.0,446.5,466.1,487.8],
    'TPP3': None,
    'TPP6': None,
    'TPPA': 0.0,
    'U10M': 3.3,
    'UWND': [3.9,4.2,4.1,4.0,4.0,3.8,3.4,2.9,0.89,-2.1,-2.8,-2.5,1.3,5.2,5.8,8.8,11.5,15.6,17.5,16.6,15.0,16.7,19.1,18.8,15.0,11.2,8.0,5.2,2.2,-0.96,-4.2],
    'V10M': -2.0,
    'VWND': [-1.2,-1.3,-1.5,-1.4,-1.6,-1.8,-1.9,-2.0,0.8,4.8,4.0,3.0,4.0,6.8,10.4,12.9,13.4,13.6,15.9,18.0,18.2,18.2,17.3,14.9,12.0,9.7,8.5,9.4,10.3,9.3,6.9],
    'WDIR': [288.1,287.5,289.9,289.9,291.8,295.1,298.8,304.9,228.5,156.9,145.4,141.3,198.5,217.7,209.6,214.7,221.1,229.1,227.9,222.9,219.9,222.8,228.3,231.9,231.7,229.3,223.5,209.0,192.6,174.4,149.1],
    'WSPD': [4.1,4.4,4.3,4.3,4.3,4.2,3.9,3.5,1.2,5.2,4.8,3.9,4.2,8.5,11.9,15.6,17.7,20.7,23.6,24.5,23.6,24.7,25.8,24.0,19.3,14.8,11.7,10.7,10.5,9.4,8.1],
    'WWND': [-28.8,-29.9,-45.4,-47.4,-62.1,-62.0,-43.6,-14.8,13.6,13.7,0.0,0.0,0.0,0.0,0.0,4.3,4.5,0.0,3.5,5.3,4.3,1.5,-0.97,-2.9,-2.3,-1.6,-0.86,-0.57,-0.93,-1.0,88.0],
    # Fix in RELH calculation changed dew_point calculations
    #'dew_point': [29.611085849971573,29.4586701744509,29.27019998327114,29.009776914500492,28.691614769871308,28.29707768409378,27.799706828016497,25.76731433060553,16.15430069456096,-8.810684446541984,-4.5307069855609825,-7.969406165725502,-7.95101193099913,0.5881826931797605,-6.581702158061773,-3.470193927454204,-10.280149861140615,-13.72670608075589,-22.892957017424294,-32.46557540216975,-43.29040951509293,-53.64650601667253,-55.39932772072072,-63.107021102632956,-65.01040987582863,-67.06593300977693,-74.55214478123997,-80.62754360799056,-90.6375076029571,-94.13591584005923,-96.56486634788743],
    'dew_point': [-5.42765482203572, -5.546825043351362, -5.6942046631419885, -5.897884865643221, -6.146778643829691, -6.455503674722991, -6.844828980687055, -8.437260184568345, -16.003036390407487, -35.91518551818217, -32.47408606577838, -35.23789531778891, -35.2230915632106, -28.373468697447066, -34.12165888183057, -31.62319884054662, -37.099274244974, -39.88180607415873, -47.31850427064765, -55.14193388932776, -64.05979181610769, -72.66290809805503, -74.12600240960018, -80.5838214977328, -82.18464297493045, -83.91613449838692, -90.24620262814281, -97.05226666666667, -97.3310214969402, -97.12193897560596, -96.56486634788743],
    'lat': 37,
    'lng': -122,
    'pressure': [993.0,984.0,973.0,958.0,940.0,918.0,891.0,855.0,810.0,766.0,722.0,662.0,588.0,520.0,458.0,402.0,351.0,304.0,262.0,224.0,189.0,158.0,130.0,106.0,84.0,65.0,49.0,35.0,23.0,13.0,4.0],
    'pressure_at_surface': 0.0
}

HOURLY_PROFILES_HOUR_2 = {
    'HPBL': 100.0,
    'HGTS': [59.20695352193937,135.82881398535508,230.2522349481686,360.414411605392,518.8055921541387,715.7651461641137,962.7815105469939,1301.743826670549,1742.0947221259023,2192.250857281424,2663.856567251226,3345.982389068354,4259.947450680663,5186.011915491956,6120.21175643276,7056.643626913428,8006.417923710241,8986.451540456597,9972.250805846712,10981.449306410641,12042.198782182653,13124.193667771762,14261.080058165118,15406.309765306385,16658.518561184595,17976.158502586513,19355.563010823662,20904.261267868987,22702.76242092459,24927.524263410254,28825.25346629527],
    'PBLH': 1474.0,
    'PRES': [993.0,984.0,975.0,961.0,943.0,921.0,896.0,862.0,820.0,778.0,736.0,678.0,608.0,544.0,486.0,432.0,383.0,339.0,299.0,263.0,230.0,200.0,174.0,150.0,130.0,112.0,96.9,83.6,72.3,62.4,53.9],
    'PRSS': 996.0,
    # fixed RELH calculation - it was off by a factor of 10 due to units
    #'RELH': [102.42075497187231,106.99940990055696,112.24258342641438,119.40509763179595,127.44170793758467,141.4049403631028,158.17153241270634,172.41920451559116,117.8221251652514,22.976815664117215,37.367340478710304,39.73810008426621,63.884695566882606,198.07703253363522,202.9497049734205,433.129048650953,444.3669459518837,580.9522520945848,505.80371957351826,451.0069790278619,313.8900183643308,161.5561808735467,122.63477535700021,42.14179258569039,38.72240258748246,38.65007617648791,18.44583359473801,8.910414657759606,2.048166503103062,1.1165462712957732,0.6242571740000024],
    'RELH': [10.242075497187231,10.699940990055696,11.224258342641438,11.940509763179595,12.744170793758467,14.14049403631028,15.817153241270634,17.241920451559116,11.78221251652514,2.2976815664117215,3.7367340478710304,3.973810008426621,6.3884695566882606,19.807703253363522,20.29497049734205,43.3129048650953,44.43669459518837,58.09522520945848,50.580371957351826,45.10069790278619,31.38900183643308,16.15561808735467,12.263477535700021,4.214179258569039,3.872240258748246,3.865007617648791,1.844583359473801,0.8910414657759606,0.2048166503103062,0.11165462712957732,0.06242571740000024],
    'RH2M': None,
    'SHGT': 112.0,
    'SPHU': [2.6,2.6,2.6,2.6,2.6,2.6,2.6,2.4,1.4,0.26,0.38,0.32,0.36,0.76,0.51,0.73,0.5,0.44,0.24,0.12,0.05,0.02,0.02,0.01,0.01,0.01,0.005,0.003,0.001,0.001,0.002],
    'T02M': 30.2,
    'TEMP': [29.2,28.3,27.3,26.0,24.6,22.5,20.2,16.9,13.6,12.0,9.5,4.8,-1.9,-8.7,-15.7,-22.1,-28.3,-34.2,-40.6,-47.8,-54.1,-57.9,-57.2,-55.7,-57.0,-59.2,-61.2,-62.2,-62.6,-62.3,-61.5],
    'TO2M': None,
    'TPOT': [303.0,302.8,302.7,302.6,302.8,302.7,302.7,302.7,303.6,306.4,308.5,310.6,312.7,314.8,316.5,319.2,322.2,325.5,328.5,330.4,333.6,341.0,356.2,373.9,387.5,400.1,413.3,429.0,446.5,466.1,487.8],
    'TPP3': None,
    'TPP6': None,
    'TPPA': 0.0,
    'U10M': 3.3,
    'UWND': [3.9,4.2,4.1,4.0,4.0,3.8,3.4,2.9,0.89,-2.1,-2.8,-2.5,1.3,5.2,5.8,8.8,11.5,15.6,17.5,16.6,15.0,16.7,19.1,18.8,15.0,11.2,8.0,5.2,2.2,-0.96,-4.2],
    'V10M': -2.0,
    'VWND': [-1.2,-1.3,-1.5,-1.4,-1.6,-1.8,-1.9,-2.0,0.8,4.8,4.0,3.0,4.0,6.8,10.4,12.9,13.4,13.6,15.9,18.0,18.2,18.2,17.3,14.9,12.0,9.7,8.5,9.4,10.3,9.3,6.9],
    'WDIR': [288.1,287.5,289.9,289.9,291.8,295.1,298.8,304.9,228.5,156.9,145.4,141.3,198.5,217.7,209.6,214.7,221.1,229.1,227.9,222.9,219.9,222.8,228.3,231.9,231.7,229.3,223.5,209.0,192.6,174.4,149.1],
    'WSPD': [4.1,4.4,4.3,4.3,4.3,4.2,3.9,3.5,1.2,5.2,4.8,3.9,4.2,8.5,11.9,15.6,17.7,20.7,23.6,24.5,23.6,24.7,25.8,24.0,19.3,14.8,11.7,10.7,10.5,9.4,8.1],
    'WWND': [-28.8,-29.9,-45.4,-47.4,-62.1,-62.0,-43.6,-14.8,13.6,13.7,0.0,0.0,0.0,0.0,0.0,4.3,4.5,0.0,3.5,5.3,4.3,1.5,-0.97,-2.9,-2.3,-1.6,-0.86,-0.57,-0.93,-1.0,88.0],
    # Fix in RELH calculation changed dew_point calculations
    #'dew_point': [29.611085849971573,29.4586701744509,29.27019998327114,29.009776914500492,28.691614769871308,28.29707768409378,27.799706828016497,25.76731433060553,16.15430069456096,-8.810684446541984,-4.5307069855609825,-7.969406165725502,-7.95101193099913,0.5881826931797605,-6.581702158061773,-3.470193927454204,-10.280149861140615,-13.72670608075589,-22.892957017424294,-32.46557540216975,-43.29040951509293,-53.64650601667253,-55.39932772072072,-63.107021102632956,-65.01040987582863,-67.06593300977693,-74.55214478123997,-80.62754360799056,-90.6375076029571,-94.13591584005923,-96.56486634788743],
    'dew_point': [-5.42765482203572, -5.546825043351362, -5.6942046631419885, -5.897884865643221, -6.146778643829691, -6.455503674722991, -6.844828980687055, -8.437260184568345, -16.003036390407487, -35.91518551818217, -32.47408606577838, -35.23789531778891, -35.2230915632106, -28.373468697447066, -34.12165888183057, -31.62319884054662, -37.099274244974, -39.88180607415873, -47.31850427064765, -55.14193388932776, -64.05979181610769, -72.66290809805503, -74.12600240960018, -80.5838214977328, -82.18464297493045, -83.91613449838692, -90.24620262814281, -97.05226666666667, -97.3310214969402, -97.12193897560596, -96.56486634788743],
    'lat': 37,
    'lng': -122,
    'pressure': [993.0,984.0,973.0,958.0,940.0,918.0,891.0,855.0,810.0,766.0,722.0,662.0,588.0,520.0,458.0,402.0,351.0,304.0,262.0,224.0,189.0,158.0,130.0,106.0,84.0,65.0,49.0,35.0,23.0,13.0,4.0],
    'pressure_at_surface': 0.0
}

HOURLY_PROFILES_ALL_HOURS_WITH_OFFSET = {
    datetime.datetime(2014, 5, 29, 17, 0): dict(HOURLY_PROFILES_HOUR_0, sunrise_hour=6, sunset_hour=18),
    datetime.datetime(2014, 5, 29, 18, 0): dict(HOURLY_PROFILES_HOUR_1, sunrise_hour=6, sunset_hour=18),
    datetime.datetime(2014, 5, 29, 19, 0): dict(HOURLY_PROFILES_HOUR_2, sunrise_hour=6, sunset_hour=18)
}

HOURLY_PROFILES_ALL_HOURS_NO_OFFSET = {
    datetime.datetime(2014, 5, 30, 0, 0): dict(HOURLY_PROFILES_HOUR_0, sunrise_hour=13, sunset_hour=25),
    datetime.datetime(2014, 5, 30, 1, 0): dict(HOURLY_PROFILES_HOUR_1, sunrise_hour=13, sunset_hour=25),
    datetime.datetime(2014, 5, 30, 2, 0): dict(HOURLY_PROFILES_HOUR_2, sunrise_hour=13, sunset_hour=25)
}

HOURLY_PROFILES_PARTIAL_WITH_OFFSET = {
    datetime.datetime(2014, 5, 29, 18, 0): dict(HOURLY_PROFILES_HOUR_1, sunrise_hour=6, sunset_hour=18)
}

HOURLY_PROFILES_PARTIAL_NO_OFFSET = {
    datetime.datetime(2014, 5, 30, 1, 0): dict(HOURLY_PROFILES_HOUR_1, sunrise_hour=13, sunset_hour=25)
}
