//var stock_map_morning = {
//  "Select a group": ["-"],
//  Banking: [
//    "TCB",
//    "VCB",
//    "BID",
//    "CTG",
//    "VPB",
//    "MBB",
//    "EIB",
//    "STB",
//    "HDB",
//    "All",
//  ],
//  "Real estate": ["ROS", "NVL", "TCH", "KDH", "All"],
//  Vingroup: ["VHM", "VRE", "VIC", "All"],
//  "Oil and Gas": ["GAS", "POW", "PXL", "All"],
//  "Food and Drink": ["SBT", "MSN", "VNM", "SAB", "All"],
//  Others: ["HPG", "REE", "PNJ", "MWG", "FPT", "VJC", "SSI", "All"],
//  "Social trend": ["-"],
//};

function changeSite(el, stock_map_morning) {
  var stock_code = document.getElementById("stock-code");
  stock_code.innerHTML = null;
  var mapping = stock_map_morning[el.value];
  mapping.reverse()
  mapping.forEach(function (code) {
    var option = document.createElement("option");
    option.value = code;
    option.text = code;
    option.selected = true;
    stock_code.add(option, stock_code[0]);
  });
}
