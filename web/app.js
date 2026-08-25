const careers = {
  student: {
    name: "文法学校学生",
    salary: 0,
    rent: 45,
    dailyCost: 2,
    requiredWorkDays: 0,
    workIncome: 18,
    workStress: 4,
    studyBonus: 1,
    description: "学习效率更高，没有固定月薪，靠零工补贴生活。",
  },
  apprentice: {
    name: "店铺学徒",
    salary: 145,
    rent: 38,
    dailyCost: 2,
    requiredWorkDays: 18,
    workIncome: 0,
    workStress: 6,
    studyBonus: 0,
    description: "收入低但稳定，正常出勤后能维持朴素生活。",
  },
  clerk: {
    name: "事务所文员",
    salary: 230,
    rent: 58,
    dailyCost: 3,
    requiredWorkDays: 18,
    workIncome: 0,
    workStress: 8,
    studyBonus: 0,
    description: "收入稳定，能攒下一点钱，但工作压力明显。",
  },
  temp_worker: {
    name: "临时工",
    salary: 0,
    rent: 35,
    dailyCost: 2,
    requiredWorkDays: 0,
    workIncome: 26,
    workStress: 7,
    studyBonus: 0,
    description: "没有固定月薪，靠每天接活赚钱，收入波动更大。",
  },
};

const namePool = {
  given: ["埃文", "伦纳德", "休伯特", "艾伦", "约书亚", "梅丽莎", "奥黛丽", "伊莱恩"],
  family: ["莫里斯", "霍尔", "格兰特", "怀特", "亚伯拉罕", "伍德", "布莱克", "斯通"],
};

const backgrounds = [
  {
    id: "lower_middle",
    family: "下层中产",
    socialClass: "普通市民",
    trait: "谨慎",
    age: [16, 19],
    careerId: "student",
    locationId: "north",
    stats: { money: 120, intelligence: 4, stress: 5, charisma: 1 },
    tags: ["下层中产出身"],
    intro: "你的家庭还算体面，但每一笔开销都需要仔细计算。",
  },
  {
    id: "worker_family",
    family: "工人家庭",
    socialClass: "下层市民",
    trait: "坚韧",
    age: [17, 22],
    careerId: "temp_worker",
    locationId: "east",
    stats: { money: 72, health: 4, stamina: 8, stress: 12, intelligence: -2 },
    tags: ["工人家庭出身"],
    intro: "你从小就知道钱来得不容易，也知道沉默有时候比抱怨有用。",
  },
  {
    id: "shop_family",
    family: "小商人家庭",
    socialClass: "小市民",
    trait: "精明",
    age: [16, 21],
    careerId: "apprentice",
    locationId: "market",
    stats: { money: 150, charisma: 4, intelligence: 1, stress: 4 },
    tags: ["小商人家庭出身"],
    intro: "你熟悉账本、讨价还价和街坊之间微妙的人情往来。",
  },
  {
    id: "clerk_family",
    family: "文职家庭",
    socialClass: "体面市民",
    trait: "守序",
    age: [18, 24],
    careerId: "clerk",
    locationId: "north",
    stats: { money: 180, intelligence: 3, charisma: 2, stress: 6 },
    tags: ["文职家庭出身"],
    intro: "你的家人相信稳定、文书、薪水和准时缴纳账单。",
  },
  {
    id: "fallen_family",
    family: "破落家庭",
    socialClass: "边缘市民",
    trait: "敏感",
    age: [17, 23],
    careerId: "temp_worker",
    locationId: "east",
    stats: { money: 38, spirituality: 3, charisma: -1, stress: 18 },
    tags: ["破落家庭出身"],
    intro: "家道下滑之后，你学会了观察别人的脸色，也更容易察觉异常。",
  },
];

const locations = {
  north: {
    name: "北区",
    description: "学校、事务所和体面住宅集中在这里，街道相对安静。",
    risk: 6,
    travelCost: 0,
    travelStamina: 3,
    tags: ["城市日常", "学习"],
  },
  market: {
    name: "市场区",
    description: "叫卖声、煤烟和零钱在这里流动，机会与麻烦都更多。",
    risk: 12,
    travelCost: 2,
    travelStamina: 5,
    tags: ["城市日常", "金钱"],
  },
  church: {
    name: "黑夜教堂",
    description: "厚重石墙隔开了街上的嘈杂，祈祷声低而稳定。",
    risk: 4,
    travelCost: 1,
    travelStamina: 4,
    tags: ["教会", "安宁"],
  },
  east: {
    name: "东区",
    description: "这里更拥挤、更潮湿，也更容易听见不该听见的事。",
    risk: 22,
    travelCost: 2,
    travelStamina: 7,
    tags: ["贫民区", "异常"],
  },
  station: {
    name: "廷根车站",
    description: "蒸汽、行李和远方消息聚在一起，让人想起城市之外。",
    risk: 14,
    travelCost: 3,
    travelStamina: 5,
    tags: ["交通", "消息"],
  },
};

const contactTemplates = {
  neighbor: {
    name: "莎伦太太",
    role: "邻居",
    locationId: "north",
    currentLocationId: "north",
    currentActivity: "在家整理房间",
    schedule: ["north", "north", "market", "north", "north", "church", "north"],
    routine: [
      { locationId: "north", activity: "在家整理房间" },
      { locationId: "north", activity: "照看走廊和邻居" },
      { locationId: "market", activity: "去市场采买" },
      { locationId: "north", activity: "和街坊聊天" },
      { locationId: "north", activity: "清点家用" },
      { locationId: "church", activity: "去教堂祈祷" },
      { locationId: "north", activity: "在家休息" },
    ],
    trust: 18,
    note: "熟悉街坊消息，愿意聊家长里短。",
  },
  newsboy: {
    name: "托比",
    role: "报童",
    locationId: "market",
    currentLocationId: "market",
    currentActivity: "沿街卖报",
    schedule: ["market", "station", "market", "north", "market", "station", "market"],
    routine: [
      { locationId: "market", activity: "沿街卖报" },
      { locationId: "station", activity: "在车站等晨报" },
      { locationId: "market", activity: "替摊主跑腿" },
      { locationId: "north", activity: "给住户送报" },
      { locationId: "market", activity: "在市场打听消息" },
      { locationId: "station", activity: "追着晚班列车卖报" },
      { locationId: "market", activity: "回市场区睡觉" },
    ],
    trust: 12,
    note: "在市场和车站附近跑动，听过不少闲话。",
  },
  priest: {
    name: "奥尔森教士",
    role: "教士",
    locationId: "church",
    currentLocationId: "church",
    currentActivity: "主持日常祈祷",
    schedule: ["church", "church", "church", "north", "church", "church", "church"],
    routine: [
      { locationId: "church", activity: "主持日常祈祷" },
      { locationId: "church", activity: "整理教堂档案" },
      { locationId: "church", activity: "接待信徒" },
      { locationId: "north", activity: "探访北区住户" },
      { locationId: "church", activity: "处理教区事务" },
      { locationId: "church", activity: "守夜祈祷" },
      { locationId: "church", activity: "安静休息" },
    ],
    trust: 8,
    note: "态度温和，但对异常话题非常谨慎。",
  },
  landlord: {
    name: "哈维先生",
    role: "房东",
    locationId: "north",
    currentLocationId: "north",
    currentActivity: "查看出租屋",
    routine: [
      { locationId: "north", activity: "查看出租屋" },
      { locationId: "market", activity: "去市场收账" },
      { locationId: "north", activity: "整理租金账本" },
      { locationId: "east", activity: "催收便宜公寓租金" },
      { locationId: "north", activity: "拜访住户" },
      { locationId: "market", activity: "和中介谈价格" },
      { locationId: "north", activity: "在家休息" },
    ],
    trust: 6,
    note: "关心租金胜过关心住户，但消息来源不少。",
  },
  clerk_boss: {
    name: "雷蒙德主管",
    role: "事务所主管",
    locationId: "north",
    currentLocationId: "north",
    currentActivity: "审阅文书",
    routine: [
      { locationId: "north", activity: "审阅文书" },
      { locationId: "north", activity: "安排文员工作" },
      { locationId: "market", activity: "拜访客户" },
      { locationId: "north", activity: "核对账册" },
      { locationId: "station", activity: "等待外地信件" },
      { locationId: "north", activity: "处理积压档案" },
      { locationId: "church", activity: "参加礼拜" },
    ],
    trust: 5,
    note: "重视效率和体面，对年轻人的耐心有限。",
  },
  shopkeeper: {
    name: "贝克兰德太太",
    role: "杂货店主",
    locationId: "market",
    currentLocationId: "market",
    currentActivity: "看守柜台",
    routine: [
      { locationId: "market", activity: "看守柜台" },
      { locationId: "market", activity: "清点货架" },
      { locationId: "station", activity: "接收货物" },
      { locationId: "market", activity: "和顾客议价" },
      { locationId: "north", activity: "给熟客送货" },
      { locationId: "market", activity: "盘点账本" },
      { locationId: "market", activity: "收摊休息" },
    ],
    trust: 10,
    note: "熟悉市场价格，也熟悉谁最近缺钱。",
  },
  baker: {
    name: "乔纳斯",
    role: "面包师",
    locationId: "market",
    currentLocationId: "market",
    currentActivity: "烘烤黑麦面包",
    routine: [
      { locationId: "market", activity: "烘烤黑麦面包" },
      { locationId: "market", activity: "凌晨揉面" },
      { locationId: "north", activity: "给学校送面包" },
      { locationId: "market", activity: "照看炉火" },
      { locationId: "east", activity: "低价处理隔夜面包" },
      { locationId: "market", activity: "准备周末订单" },
      { locationId: "church", activity: "捐出剩余面包" },
    ],
    trust: 9,
    note: "起得很早，常听见街道还没醒时的动静。",
  },
  porter: {
    name: "马丁",
    role: "搬运工",
    locationId: "station",
    currentLocationId: "station",
    currentActivity: "搬运行李",
    routine: [
      { locationId: "station", activity: "搬运行李" },
      { locationId: "station", activity: "卸下货箱" },
      { locationId: "market", activity: "替商贩搬货" },
      { locationId: "station", activity: "等候晚班列车" },
      { locationId: "east", activity: "回东区住处" },
      { locationId: "station", activity: "修整手推车" },
      { locationId: "market", activity: "喝一杯廉价啤酒" },
    ],
    trust: 7,
    note: "力气大，眼神直，知道车站货物的去向。",
  },
  coachman: {
    name: "伍德车夫",
    role: "出租马车夫",
    locationId: "station",
    currentLocationId: "station",
    currentActivity: "等候乘客",
    routine: [
      { locationId: "station", activity: "等候乘客" },
      { locationId: "north", activity: "送客去北区" },
      { locationId: "market", activity: "在市场补给草料" },
      { locationId: "station", activity: "接夜车乘客" },
      { locationId: "east", activity: "绕路避开拥堵" },
      { locationId: "north", activity: "给常客送信" },
      { locationId: "station", activity: "修整马具" },
    ],
    trust: 6,
    note: "走遍廷根街道，知道哪条路什么时候不该去。",
  },
  washerwoman: {
    name: "露西",
    role: "洗衣女工",
    locationId: "east",
    currentLocationId: "east",
    currentActivity: "在院里洗衣",
    routine: [
      { locationId: "east", activity: "在院里洗衣" },
      { locationId: "north", activity: "给住户送回衣物" },
      { locationId: "east", activity: "晾晒床单" },
      { locationId: "market", activity: "购买肥皂" },
      { locationId: "east", activity: "替工友缝补衣服" },
      { locationId: "north", activity: "收取脏衣篮" },
      { locationId: "church", activity: "参加晚祷" },
    ],
    trust: 11,
    note: "常出入不同住户家门，知道很多沉默的生活细节。",
  },
  factory_worker: {
    name: "阿尔弗雷德",
    role: "工厂工人",
    locationId: "east",
    currentLocationId: "east",
    currentActivity: "赶去工厂",
    routine: [
      { locationId: "east", activity: "赶去工厂" },
      { locationId: "east", activity: "在车间做工" },
      { locationId: "market", activity: "购买晚饭" },
      { locationId: "east", activity: "排队领工钱" },
      { locationId: "east", activity: "修补靴子" },
      { locationId: "market", activity: "找零工消息" },
      { locationId: "east", activity: "睡到很晚" },
    ],
    trust: 8,
    note: "疲惫但敏锐，知道东区工人间流传的消息。",
  },
  doctor: {
    name: "艾琳医生",
    role: "诊所医生",
    locationId: "north",
    currentLocationId: "north",
    currentActivity: "接诊病人",
    routine: [
      { locationId: "north", activity: "接诊病人" },
      { locationId: "east", activity: "去东区出诊" },
      { locationId: "north", activity: "整理药柜" },
      { locationId: "market", activity: "采购药材" },
      { locationId: "north", activity: "写病历" },
      { locationId: "east", activity: "探望长期病人" },
      { locationId: "church", activity: "与教士交谈" },
    ],
    trust: 9,
    note: "能分清普通疲惫和不太普通的症状。",
  },
  constable: {
    name: "米勒巡警",
    role: "巡警",
    locationId: "north",
    currentLocationId: "north",
    currentActivity: "沿街巡逻",
    routine: [
      { locationId: "north", activity: "沿街巡逻" },
      { locationId: "market", activity: "处理市场争执" },
      { locationId: "station", activity: "查看车站布告" },
      { locationId: "east", activity: "短暂巡查东区" },
      { locationId: "north", activity: "回警署写报告" },
      { locationId: "market", activity: "询问摊贩" },
      { locationId: "church", activity: "在教堂外值守" },
    ],
    trust: 4,
    note: "相信秩序，也相信麻烦最好尽早被按住。",
  },
  teacher: {
    name: "卡特老师",
    role: "学校教师",
    locationId: "north",
    currentLocationId: "north",
    currentActivity: "准备课程",
    routine: [
      { locationId: "north", activity: "准备课程" },
      { locationId: "north", activity: "批改作业" },
      { locationId: "market", activity: "购买墨水" },
      { locationId: "north", activity: "辅导学生" },
      { locationId: "station", activity: "寄出信件" },
      { locationId: "north", activity: "整理教案" },
      { locationId: "church", activity: "参加礼拜" },
    ],
    trust: 12,
    note: "重视努力，也看得出一个学生最近是否心神不宁。",
  },
  librarian: {
    name: "珀西瓦尔",
    role: "图书管理员",
    locationId: "north",
    currentLocationId: "north",
    currentActivity: "整理书架",
    routine: [
      { locationId: "north", activity: "整理书架" },
      { locationId: "north", activity: "登记借阅记录" },
      { locationId: "market", activity: "寻找旧书" },
      { locationId: "north", activity: "修补破损书页" },
      { locationId: "station", activity: "接收外地期刊" },
      { locationId: "north", activity: "清点禁借书目" },
      { locationId: "north", activity: "安静读书" },
    ],
    trust: 7,
    note: "记性很好，对奇怪的借阅记录尤其敏感。",
  },
  seamstress: {
    name: "玛丽安",
    role: "裁缝",
    locationId: "market",
    currentLocationId: "market",
    currentActivity: "修改衣袖",
    routine: [
      { locationId: "market", activity: "修改衣袖" },
      { locationId: "north", activity: "给客户量尺寸" },
      { locationId: "market", activity: "采购布料" },
      { locationId: "east", activity: "探望妹妹" },
      { locationId: "market", activity: "赶制订单" },
      { locationId: "north", activity: "送还礼服" },
      { locationId: "market", activity: "整理针线盒" },
    ],
    trust: 10,
    note: "手巧嘴严，知道谁最近换了不合身份的衣服。",
  },
  courier: {
    name: "费恩",
    role: "信使",
    locationId: "station",
    currentLocationId: "station",
    currentActivity: "分拣信件",
    routine: [
      { locationId: "station", activity: "分拣信件" },
      { locationId: "north", activity: "投递公文" },
      { locationId: "market", activity: "给商铺送信" },
      { locationId: "east", activity: "寻找收信人" },
      { locationId: "station", activity: "登记退信" },
      { locationId: "north", activity: "送急件" },
      { locationId: "market", activity: "听商人抱怨" },
    ],
    trust: 6,
    note: "脚程快，知道很多信件没有送到哪里。",
  },
  beggar: {
    name: "老昆西",
    role: "流浪者",
    locationId: "east",
    currentLocationId: "east",
    currentActivity: "靠墙晒太阳",
    routine: [
      { locationId: "east", activity: "靠墙晒太阳" },
      { locationId: "market", activity: "在人群边乞讨" },
      { locationId: "church", activity: "领取救济汤" },
      { locationId: "east", activity: "躲在桥洞下" },
      { locationId: "station", activity: "翻找遗落行李" },
      { locationId: "market", activity: "听醉汉说话" },
      { locationId: "east", activity: "很早睡下" },
    ],
    trust: 5,
    note: "看似糊涂，却经常看到别人不会注意的角落。",
  },
  book_vendor: {
    name: "伊诺克",
    role: "旧书贩",
    locationId: "market",
    currentLocationId: "market",
    currentActivity: "摆出旧书摊",
    routine: [
      { locationId: "market", activity: "摆出旧书摊" },
      { locationId: "north", activity: "收购旧教材" },
      { locationId: "market", activity: "整理书箱" },
      { locationId: "station", activity: "等待外地书包裹" },
      { locationId: "market", activity: "低声推荐冷门书" },
      { locationId: "north", activity: "拜访藏书人" },
      { locationId: "market", activity: "收摊清账" },
    ],
    trust: 8,
    note: "能找到廉价书，也能找到不该随便读的书。",
  },
  night_watchman: {
    name: "格林守夜人",
    role: "守夜人",
    locationId: "north",
    currentLocationId: "north",
    currentActivity: "白天补觉",
    routine: [
      { locationId: "north", activity: "白天补觉" },
      { locationId: "market", activity: "黄昏巡街" },
      { locationId: "east", activity: "避开深巷巡逻" },
      { locationId: "station", activity: "查看末班车" },
      { locationId: "north", activity: "敲响夜间报时" },
      { locationId: "market", activity: "劝走醉客" },
      { locationId: "north", activity: "交接巡夜记录" },
    ],
    trust: 5,
    note: "昼夜颠倒，比多数人更熟悉夜里的廷根。",
  },
};

const investigations = [
  {
    id: "landlord_unusual",
    contactId: "neighbor",
    locationId: "north",
    minTrust: 10,
    risk: 6,
    result: "莎伦太太压低声音告诉你，最近房东频繁催租，似乎不只是缺钱。",
    effects: { intelligence: 1, stress: 1 },
    trustChange: 3,
    addClues: [
      {
        id: "landlord_unusual",
        title: "房东的异常催租",
        text: "房东催租频率过高，背后可能另有压力来源。",
      },
    ],
  },
  {
    id: "old_hat_man",
    contactId: "newsboy",
    locationId: "market",
    requiresAnyClue: ["missing_notice", "old_button"],
    minTrust: 8,
    risk: 12,
    result: "托比说有个戴旧礼帽的人最近总在车站和东区之间来回，像是在找什么。",
    effects: { intelligence: 1, mysticism: 1, stress: 2 },
    trustChange: 4,
    addClues: [
      {
        id: "old_hat_man",
        title: "戴旧礼帽的人",
        text: "有人在车站和东区之间来回活动，可能与失踪启事有关。",
      },
    ],
  },
  {
    id: "avoid_east_night",
    contactId: "priest",
    locationId: "church",
    requiresAnyClue: ["wall_symbol", "newspaper_overlap", "being_followed"],
    minTrust: 8,
    risk: 4,
    result: "奥尔森教士没有回答符号的含义，只让你记住：夜晚不要独自前往东区小巷。",
    effects: { mysticism: 2, spirituality: 1, stress: 1 },
    trustChange: 2,
    addClues: [
      {
        id: "avoid_east_night",
        title: "不要夜探东区",
        text: "教士回避了真相，但明确警告你不要独自深入东区。",
      },
    ],
  },
  {
    id: "east_safe_route",
    contactId: "newsboy",
    locationId: "market",
    requiresDeductions: ["east_case_pattern"],
    minTrust: 12,
    risk: 16,
    result: "托比想了很久，给你画出一条避开巡警和醉汉的东区小路。那条路靠近几起异常消息的交汇处。",
    effects: { intelligence: 1, stress: 2 },
    trustChange: 3,
    addClues: [
      {
        id: "east_safe_route",
        title: "通往东区小巷的安全路线",
        text: "一条相对安全的东区路线，可能用于后续深入调查。",
      },
    ],
  },
];

const deductionRules = [
  {
    id: "east_case_pattern",
    title: "东区异常并非孤立事件",
    requiresAny: [
      ["wall_symbol", "being_followed"],
      ["missing_notice", "newspaper_overlap"],
      ["old_button", "old_hat_man"],
    ],
    text: "墙角符号、失踪消息和可疑人物可能都指向东区。它不像一桩偶发事件，更像有人在固定范围内活动。",
    effects: { intelligence: 2, mysticism: 2, stress: 3 },
    addTags: ["怀疑东区异常"],
  },
  {
    id: "church_knows_more",
    title: "黑夜教堂知道更多",
    requiresAll: ["church_warning", "avoid_east_night"],
    text: "教士的提醒不是普通劝告。黑夜教堂大概率知道东区异常的性质，只是不愿向普通人公开。",
    effects: { mysticism: 2, spirituality: 1, stress: 2 },
    addTags: ["怀疑教会隐情"],
  },
];

const storyArcLabels = {
  unnoticed: "尚未开始",
  rumor: "异常传闻",
  clue_found: "发现线索",
  npc_contact: "认识相关人物",
  decision: "等待选择",
  reported: "已举报",
  concealed: "已隐瞒",
  committed: "追查到底",
  coin: "拿到旧币",
  dream: "符号之梦",
  first_contact: "初涉非凡",
};

const eventGraphs = {
  ordinaryLife: {
    title: "普通生活",
    type: "ordinary",
    nodes: [
      { id: "ordinary_rain", eventId: "rainy_cold", label: "冷雨" },
      { id: "ordinary_book", eventId: "cheap_book", label: "旧书摊" },
      { id: "ordinary_bell", eventId: "church_bell", label: "钟声" },
      { id: "ordinary_rent", eventId: "landlord_pressure", label: "房租压力", repeatable: true },
      { id: "ordinary_pickpocket", eventId: "market_pickpocket", label: "市场扒手" },
      { id: "ordinary_overtime", eventId: "work_overtime", label: "加班要求" },
      { id: "ordinary_exam", eventId: "study_exam", label: "课堂测验" },
      { id: "ordinary_neighbor_soup", eventId: "neighbor_soup", label: "邻居热汤" },
      { id: "ordinary_market_price", eventId: "market_price_rise", label: "市场涨价" },
      { id: "ordinary_home_leak", eventId: "home_leak", label: "屋顶漏水" },
    ],
  },
  abnormalDisappearance: {
    title: "异常失踪",
    type: "abnormal",
    nodes: [
      { id: "abnormal_notice", eventId: "station_notice", label: "失踪启事" },
      {
        id: "abnormal_overlap",
        eventId: "newspaper_overlap",
        label: "报纸重叠",
        afterNodes: ["abnormal_notice"],
      },
      {
        id: "abnormal_symbol",
        eventId: "strange_symbol",
        label: "墙角符号",
        afterNodes: ["abnormal_overlap"],
      },
      {
        id: "abnormal_followed",
        eventId: "east_followed",
        label: "身后脚步",
        afterNodes: ["abnormal_symbol"],
      },
      {
        id: "abnormal_decision",
        eventId: "disappearance_decision",
        label: "失踪案选择",
        afterNodes: ["abnormal_followed"],
      },
    ],
  },
  mysticContact: {
    title: "非凡接触",
    type: "mystic",
    nodes: [
      {
        id: "mystic_coin",
        eventId: "priest_coin",
        label: "教堂旧币",
        afterNodes: ["abnormal_decision"],
      },
      {
        id: "mystic_deep",
        eventId: "east_deep_night",
        label: "深夜东区",
        afterNodes: ["abnormal_decision"],
      },
      {
        id: "mystic_dream",
        eventId: "symbol_dream",
        label: "符号之梦",
      },
      {
        id: "mystic_beyonder",
        eventId: "first_beyonder",
        label: "初涉非凡",
        afterNodes: ["mystic_dream"],
      },
    ],
  },
};

const eventGraphNodes = Object.values(eventGraphs).flatMap((graph) =>
  graph.nodes.map((node) => ({ ...node, graphId: graph.title, type: graph.type })),
);

const actions = {
  study: {
    name: "学习",
    summary: "你认真学习了一整天，脑子有些疲惫，但知识确实增长了。",
    effects: { intelligence: 2, stamina: -8, stress: 4 },
  },
  work: {
    name: "工作",
    summary: "你把一天交给了工作，账本上的数字因此稍微好看了一些。",
    effects: { stamina: -12 },
  },
  rest: {
    name: "休息",
    summary: "你让自己慢下来，睡眠和热茶让状态恢复了一些。",
    effects: { health: 4, stamina: 18, stress: -10 },
  },
  social: {
    name: "社交",
    summary: "你和几位熟人聊了很久，对这座城市的日常有了更多感觉。",
    effects: { charisma: 2, money: -6, stress: -4 },
  },
  wander: {
    name: "闲逛",
    summary: "你在廷根的街道上走了很久，煤烟、马车和报童的叫卖声混在一起。",
    effects: { stamina: -6, stress: -1 },
  },
  investigate: {
    name: "调查",
    summary: "你试着把零碎线索串起来，并向合适的人打听消息。",
    effects: { stamina: -8, stress: 3 },
  },
  deduce: {
    name: "推理",
    summary: "你把收集到的线索摊开，试图找出它们之间真正的联系。",
    effects: { stamina: -5, stress: 2 },
  },
};

const events = [
  {
    id: "rainy_cold",
    title: "冷雨",
    text: "傍晚突然下起冷雨，你没来得及躲开，回家后感到一阵寒意。",
    chance: 18,
    weight: 3,
    choices: [
      {
        label: "赶紧回家",
        result: "你缩紧外套一路快走，虽然狼狈，但没有继续在雨里消耗体力。",
        effects: { health: -2, stamina: -1 },
      },
      {
        label: "找地方避雨",
        result: "你躲进一家小店，花了几便士买热饮，身体舒服了些。",
        effects: { money: -4, stress: -2 },
      },
    ],
  },
  {
    id: "cheap_book",
    title: "旧书摊",
    locations: ["market", "north"],
    text: "旧书摊上有一本便宜的历史读物，你犹豫片刻还是买了下来。",
    chance: 12,
    weight: 2,
    choices: [
      {
        label: "买下来",
        result: "书页发黄，但里面关于鲁恩旧贵族的段落很有意思。",
        effects: { money: -5, intelligence: 2 },
        addTags: ["买过旧书"],
      },
      {
        label: "只翻几页",
        result: "你记住了几个陌生名字，把钱留在了口袋里。",
        effects: { intelligence: 1 },
      },
    ],
  },
  {
    id: "church_bell",
    title: "钟声",
    locations: ["church", "north"],
    text: "黑夜教堂的钟声在雾气中响起，你短暂地感到安心。",
    chance: 10,
    weight: 2,
    choices: [
      {
        label: "进入教堂",
        result: "你在长椅上坐了一会儿，安静让脑子里的杂音淡了下去。",
        effects: { stress: -5, spirituality: 1 },
        addTags: ["去过黑夜教堂"],
      },
      {
        label: "继续赶路",
        result: "钟声被马车声抛在身后，你只是短暂地平静了一些。",
        effects: { stress: -2 },
      },
    ],
  },
  {
    id: "strange_symbol",
    title: "墙角符号",
    locations: ["east", "market"],
    text: "你在小巷墙角看见一个奇怪符号，很快又被人用灰浆抹去。",
    chance: 8,
    weight: 1,
    minDay: 5,
    choices: [
      {
        label: "记下形状",
        result: "你把符号草草画在纸上。它不像装饰，更像某种标记。",
        effects: { mysticism: 2, stress: 3 },
        addTags: ["见过神秘符号"],
        addClues: [
          {
            id: "wall_symbol",
            title: "被抹去的墙角符号",
            text: "你记下了一个不像装饰的符号，但暂时不知道它代表什么。",
          },
        ],
      },
      {
        label: "立刻离开",
        result: "你压下好奇心，决定别靠近看不懂的麻烦。",
        effects: { stress: -1 },
        addTags: ["避开异常"],
      },
    ],
  },
  {
    id: "landlord_pressure",
    title: "房租",
    locations: ["east", "north"],
    monthlyFlag: "landlordPressureHandled",
    text: "房东提醒你下周要交房租，语气礼貌，但没有商量余地。",
    chance: 15,
    weight: 2,
    minDay: 8,
    choices: [
      {
        label: "提前支付",
        result: "你提前付清一部分房租，钱包薄了，但心里踏实不少。",
        effects: { money: -30, stress: -4 },
        rentPayment: 30,
        addTags: ["房租已缓解"],
      },
      {
        label: "请求宽限",
        result: "房东答应多给你几天，但你能感觉到对方的耐心有限。",
        effects: { charisma: 1, stress: 5 },
        addTags: ["欠下房租压力"],
      },
    ],
  },
  {
    id: "station_notice",
    title: "车站布告",
    locations: ["station"],
    text: "车站布告栏前围着几个人，一张失踪寻人启事被雨水泡得卷边。",
    chance: 22,
    weight: 3,
    minDay: 3,
    choices: [
      {
        label: "仔细阅读",
        result: "你记下了失踪者的姓氏。那名字似乎在哪份报纸上见过。",
        effects: { intelligence: 1, stress: 1 },
        addTags: ["见过失踪启事"],
        addClues: [
          {
            id: "missing_notice",
            title: "车站失踪启事",
            text: "失踪者姓氏和一份旧报纸上的边角消息隐约对得上。",
          },
        ],
      },
      {
        label: "匆匆离开",
        result: "你没有久留。车站总让你觉得会被卷进别人的人生。",
        effects: { stress: -1 },
      },
    ],
  },
  {
    id: "work_overtime",
    title: "加班要求",
    locations: ["north", "market", "east"],
    text: "掌柜或上司临时要求你多留一会儿。活不算难，但这一天会被拖得很长。",
    chance: 18,
    weight: 2,
    minDay: 6,
    choices: [
      {
        label: "留下加班",
        result: "你把额外的活做完，回家时街灯已经亮起。对方记住了你的可靠。",
        effects: { stamina: -8, stress: 4, money: 4 },
        addTags: ["认真加班"],
      },
      {
        label: "准时离开",
        result: "你婉拒了加班。身体轻松一点，但对方的脸色不太好看。",
        effects: { stress: 2, stamina: 3 },
        addTags: ["拒绝加班"],
      },
    ],
  },
  {
    id: "study_exam",
    title: "课堂测验",
    locations: ["north"],
    text: "老师突然安排了一次小测验。题目不算刁钻，但足够看出最近有没有用功。",
    chance: 16,
    weight: 2,
    minDay: 7,
    choices: [
      {
        label: "认真答题",
        result: "你答得不错。老师多看了你一眼，像是记住了这个名字。",
        effects: { intelligence: 2, stress: 2 },
        addTags: ["课堂表现不错"],
      },
      {
        label: "勉强应付",
        result: "你写完了大半，但心里知道有几题只是猜的。",
        effects: { stress: 1 },
        addTags: ["测验应付过去"],
      },
    ],
  },
  {
    id: "neighbor_soup",
    title: "邻居热汤",
    locations: ["north"],
    requiresContacts: { neighbor: 18 },
    text: "莎伦太太敲门送来一碗热汤，说是多煮了一些。屋里一下子有了生活的气味。",
    chance: 18,
    weight: 2,
    minDay: 5,
    choices: [
      {
        label: "道谢收下",
        result: "热汤让胃里舒服了些。你们顺便聊了几句楼里的琐事。",
        effects: { health: 2, stress: -3 },
        trustEffects: { neighbor: 2 },
      },
      {
        label: "回送一点小礼",
        result: "你把仅有的一点点点心回送过去。她笑了笑，说你是个懂礼貌的孩子。",
        effects: { money: -2, stress: -2 },
        trustEffects: { neighbor: 4 },
      },
    ],
  },
  {
    id: "market_price_rise",
    title: "市场涨价",
    locations: ["market"],
    text: "面包、煤油和廉价肉的价格都涨了一点。摊贩说最近货运不稳，谁也没办法。",
    chance: 20,
    weight: 3,
    minDay: 12,
    choices: [
      {
        label: "照常购买",
        result: "你咬牙按原计划买下生活用品。钱少了，但晚饭至少没有缩水。",
        effects: { money: -6, stress: 1 },
      },
      {
        label: "缩减开销",
        result: "你只买了最便宜的东西。账面好看一点，肚子却没那么诚实。",
        effects: { money: -2, stress: 3 },
        lifeEffects: { nutrition: -4 },
        addTags: ["压缩饮食"],
      },
    ],
  },
  {
    id: "home_leak",
    title: "屋顶漏水",
    locations: ["north", "east"],
    text: "夜里雨声变得不对劲。你发现屋角正在渗水，床边的地板已经湿了一片。",
    chance: 14,
    weight: 2,
    minDay: 15,
    choices: [
      {
        label: "自己修补",
        result: "你折腾到半夜才勉强堵住漏水处。省下了钱，却没睡好。",
        effects: { stamina: -5, stress: 2 },
        lifeEffects: { sleep: -8, fatigue: 8, comfort: 1 },
      },
      {
        label: "找人修理",
        result: "修理工动作很快，收费也很快。至少今晚不用担心雨水滴到床上。",
        effects: { money: -10, stress: -2 },
        lifeEffects: { comfort: 5 },
      },
    ],
  },
  {
    id: "market_pickpocket",
    title: "市场扒手",
    locations: ["market"],
    text: "人群突然推搡起来，你感觉有人碰了一下你的外套口袋。",
    chance: 18,
    weight: 3,
    choices: [
      {
        label: "立刻抓住对方",
        result: "你抓住了一个瘦小青年，对方挣扎着逃走，只掉下一枚旧纽扣。",
        effects: { stamina: -4, stress: 3 },
        addTags: ["捡到旧纽扣"],
        addClues: [
          {
            id: "old_button",
            title: "刻痕旧纽扣",
            text: "纽扣背面有细小刻痕，像是某个团体的暗记。",
          },
        ],
      },
      {
        label: "先检查钱包",
        result: "你护住了钱袋，虽然没损失什么，但心情糟了不少。",
        effects: { stress: 2 },
      },
    ],
  },
  {
    id: "newspaper_overlap",
    title: "报纸边角",
    locations: ["north", "market"],
    requiresAnyClue: ["missing_notice", "old_button"],
    text: "你在报纸边角看到一则短讯：有人在东区附近失踪，警方只说还在调查。",
    chance: 24,
    weight: 3,
    minDay: 6,
    choices: [
      {
        label: "剪下报纸",
        result: "你把那块报纸折好收起。几条毫不起眼的消息开始互相牵连。",
        effects: { mysticism: 1, intelligence: 1, stress: 2 },
        addClues: [
          {
            id: "newspaper_overlap",
            title: "互相重叠的失踪消息",
            text: "车站启事、旧纽扣和报纸短讯之间可能有联系。",
          },
        ],
      },
      {
        label: "当作巧合",
        result: "你告诉自己这只是城市里每天都会发生的不幸。",
        effects: { stress: -1 },
      },
    ],
  },
  {
    id: "church_warning",
    title: "温和警告",
    locations: ["church"],
    requiresAnyClue: ["wall_symbol", "newspaper_overlap"],
    text: "一位教士注意到你手里的纸片，平静地提醒你：有些事情不要独自追查。",
    chance: 28,
    weight: 3,
    minDay: 8,
    choices: [
      {
        label: "询问原因",
        result: "教士没有解释，只建议你遇到异常时先来教堂。你听不懂，但记住了这句话。",
        effects: { mysticism: 2, spirituality: 1, stress: 2 },
        addTags: ["被教士提醒"],
        addClues: [
          {
            id: "church_warning",
            title: "教士的提醒",
            text: "黑夜教堂似乎知道一些异常事件，但不会轻易向普通人说明。",
          },
        ],
      },
      {
        label: "停止追问",
        result: "你把问题咽了回去。沉默让气氛安全了一点，也让疑问更重了。",
        effects: { stress: 1 },
        addTags: ["压下疑问"],
      },
    ],
  },
  {
    id: "east_followed",
    title: "身后脚步",
    locations: ["east"],
    requiresClues: ["wall_symbol"],
    text: "你经过那条小巷时，身后的脚步声忽然和你的步伐保持了同样节奏。",
    chance: 26,
    weight: 2,
    minDay: 10,
    choices: [
      {
        label: "拐进人多的街道",
        result: "你混进人群，脚步声消失了。你的掌心出了汗。",
        effects: { stress: 4, stamina: -3 },
        addClues: [
          {
            id: "being_followed",
            title: "东区被跟踪",
            text: "接近墙角符号之后，你似乎被某人注意到了。",
          },
        ],
      },
      {
        label: "回头确认",
        result: "你只看到雾气和潮湿砖墙，但那种被盯着的感觉没有消失。",
        effects: { stress: 7, mysticism: 1 },
        addTags: ["感到被注视"],
      },
    ],
  },
  {
    id: "neighbor_private_rent",
    title: "门缝里的账单",
    locations: ["north"],
    requiresContacts: { neighbor: 28 },
    requiresClues: ["landlord_unusual"],
    minLocationReputation: 5,
    onceTag: "莎伦太太透露账单",
    text: "莎伦太太确认走廊没人后，给你看了一眼房东夹在账本里的催款单。收款人名字被墨水涂掉了。",
    chance: 32,
    weight: 3,
    minDay: 9,
    choices: [
      {
        label: "记住收款格式",
        result: "你记下了账单上的格式和印章。莎伦太太有些紧张，但还是相信你不会乱说。",
        effects: { intelligence: 2, stress: 2 },
        trustEffects: { neighbor: 2 },
        addTags: ["莎伦太太透露账单"],
        addClues: [
          {
            id: "marked_rent_bill",
            title: "被涂掉名字的催款单",
            text: "房东的压力来自一张格式古怪的催款单，收款人名字被刻意遮住。",
          },
        ],
      },
      {
        label: "劝她别卷进来",
        result: "你没有追问更多。莎伦太太松了口气，对你的谨慎多了一点好感。",
        effects: { stress: -2 },
        trustEffects: { neighbor: 4 },
        addTags: ["保护邻居"],
      },
    ],
  },
  {
    id: "newsboy_hidden_note",
    title: "报童的纸条",
    locations: ["market", "station"],
    requiresContacts: { newsboy: 24 },
    requiresAnyClue: ["old_hat_man", "old_button"],
    minLocationReputation: 4,
    onceTag: "托比递来纸条",
    text: "托比从报纸夹层里抽出一张皱纸条，说戴旧礼帽的人总在固定时辰出现。",
    chance: 30,
    weight: 3,
    minDay: 10,
    choices: [
      {
        label: "收下纸条",
        result: "纸条上写着几个时间和地点。你意识到这不是闲话，而是一条可以追踪的路线。",
        effects: { intelligence: 2, stress: 3 },
        trustEffects: { newsboy: 2 },
        addTags: ["托比递来纸条"],
        addClues: [
          {
            id: "hat_man_schedule",
            title: "旧礼帽人的出没时刻",
            text: "旧礼帽人会在车站和东区之间按固定时段出现，像是在等待交接。",
          },
        ],
      },
      {
        label: "给他买热饮",
        result: "托比没有多说，但把纸条留在了你手边。他看上去没那么害怕了。",
        effects: { money: -3, stress: -1 },
        trustEffects: { newsboy: 5 },
        addTags: ["照顾托比"],
      },
    ],
  },
  {
    id: "priest_back_room",
    title: "教堂后室",
    locations: ["church"],
    requiresContacts: { priest: 22 },
    requiresDeductions: ["east_case_pattern"],
    onceTag: "进入教堂后室",
    text: "奥尔森教士领你穿过侧门。后室里没有神秘仪式，只有厚厚的档案和几盏安静的灯。",
    chance: 35,
    weight: 2,
    minDay: 12,
    choices: [
      {
        label: "请求查看档案",
        result: "教士只允许你看其中一页。那页记录证明，东区异常至少持续了三个月。",
        effects: { mysticism: 2, spirituality: 2, stress: 2 },
        trustEffects: { priest: 2 },
        addTags: ["进入教堂后室"],
        addClues: [
          {
            id: "church_archive",
            title: "教会档案的缺页记录",
            text: "教会档案显示东区异常有连续记录，但关键页码缺失。",
          },
        ],
      },
      {
        label: "只询问自保办法",
        result: "教士教你记住几个避险原则。你没有更接近真相，但暂时更安全。",
        effects: { spirituality: 2, stress: -3 },
        exposureChange: -4,
        addTags: ["学会避险原则"],
      },
    ],
  },
  {
    id: "watched_by_unknown",
    title: "被人记住",
    locations: ["east", "station", "market"],
    minInvestigationExposure: 18,
    onceTag: "被未知势力注意",
    text: "你开始意识到，自己问过的问题正在被别人记住。某些目光会在你转身时移开。",
    chance: 36,
    weight: 4,
    minDay: 11,
    choices: [
      {
        label: "暂时收手",
        result: "你放慢追查，把几天时间花在普通生活上。危险感没有消失，但不再贴得那么近。",
        effects: { stress: -4, mysticism: -1 },
        exposureChange: -8,
        addTags: ["被未知势力注意"],
      },
      {
        label: "反向观察",
        result: "你装作没有发现，反而记住了几个可疑面孔。代价是你这一晚几乎没睡。",
        effects: { intelligence: 2, stress: 6, stamina: -5 },
        exposureChange: 4,
        addClues: [
          {
            id: "watchers_faces",
            title: "可疑的观察者",
            text: "你记住了几个似乎在暗中观察你的人，其中一人常出现在车站附近。",
          },
        ],
      },
    ],
  },
  {
    id: "disappearance_decision",
    title: "失踪案的选择",
    locations: ["north", "church", "station"],
    requiresDeductions: ["east_case_pattern"],
    onceTag: "做出失踪案选择",
    text: "失踪启事、旧纽扣、报纸短讯和东区线索终于串成一条线。现在你必须决定，自己在这件事里到底站在哪里。",
    chance: 46,
    weight: 5,
    minDay: 14,
    choices: [
      {
        label: "举报给教会",
        result: "你把整理好的线索交给黑夜教堂。教士没有承诺什么，但你看见他立刻锁上了后室的门。",
        effects: { stress: -5, spirituality: 2 },
        exposureChange: -10,
        trustEffects: { priest: 6, newsboy: -2 },
        addTags: ["做出失踪案选择", "向教会举报"],
      },
      {
        label: "暂时隐瞒",
        result: "你把线索藏进衣柜深处，决定先保住普通生活。可秘密不会因为被藏好就变轻。",
        effects: { stress: 4, stamina: 3 },
        exposureChange: -4,
        addTags: ["做出失踪案选择", "隐瞒失踪线索"],
      },
      {
        label: "调查到底",
        result: "你没有把线索交出去，也没有停手。这个决定让你更接近真相，也更接近危险。",
        effects: { intelligence: 2, mysticism: 2, stress: 6 },
        exposureChange: 8,
        trustEffects: { newsboy: 4 },
        addTags: ["做出失踪案选择", "决定追到底"],
      },
    ],
  },
  {
    id: "priest_coin",
    title: "教堂的旧硬币",
    locations: ["church"],
    requiresTags: ["向教会举报"],
    onceTag: "拿到教堂旧币",
    text: "奥尔森教士在教堂后室单独见你。他沉默了很久，把一枚褐色的旧硬币放在桌上——比看上去更沉。",
    chance: 60,
    weight: 4,
    minDay: 16,
    choices: [
      {
        label: "收下硬币",
        result: "你伸手拿起硬币。教士说：如果有一天你开始做奇怪的梦，就带着它回来。",
        effects: { spirituality: 3, mysticism: 2, stress: 3 },
        trustEffects: { priest: 3 },
        addTags: ["拿到教堂旧币"],
        addClues: [
          {
            id: "church_coin",
            title: "教士给的旧硬币",
            text: "一枚看似普通的旧硬币，比看上去更沉，似乎与灵性有关。",
          },
        ],
      },
      {
        label: "只问问题",
        result: "你没有碰硬币，只问它是什么。教士没有回答，但你看得出他松了口气，也看得出他有些失望。",
        effects: { mysticism: 1, spirituality: 1 },
        trustEffects: { priest: -1 },
      },
    ],
  },
  {
    id: "east_deep_night",
    title: "深夜东区",
    locations: ["east"],
    requiresTags: ["决定追到底"],
    onceTag: "深夜探过东区",
    text: "你没有告诉任何人，独自在午夜走进了东区的深巷。雾气里，你看见一扇门缝透出不属于蜡烛的微光。",
    chance: 55,
    weight: 4,
    minDay: 16,
    choices: [
      {
        label: "凑近那扇门",
        result: "你凑近门缝，看见里面的人在纸上画着与墙角符号一模一样的东西。你记住了这个画面。",
        effects: { mysticism: 3, stress: 7, stamina: -6 },
        exposureChange: 10,
        addTags: ["深夜探过东区"],
        addClues: [
          {
            id: "deep_night_route",
            title: "深夜东区的可疑仪式",
            text: "午夜东区有人在举行与墙角符号相关的仪式，位置你已经记住。",
          },
        ],
      },
      {
        label: "立刻离开",
        result: "理智把你拽了回去。你快步离开东区，但那个符号的影子在你脑子里转了一整夜。",
        effects: { stress: 4, stamina: -3 },
        addTags: ["深夜探过东区"],
      },
    ],
  },
  {
    id: "symbol_dream",
    title: "符号之梦",
    locations: ["north", "east", "church"],
    requiresAnyClue: ["church_coin", "deep_night_route"],
    onceTag: "做过符号之梦",
    text: "夜里你梦见自己走在一条没有灯的地下通道里，两边的墙上画满了同样的符号，一直延伸到看不见的深处。",
    chance: 65,
    weight: 4,
    minDay: 20,
    choices: [
      {
        label: "在梦里记住路线",
        result: "你强迫自己记住每一个拐弯。醒来时窗外天还没亮，而你记得通道的尽头是一扇铁门。",
        effects: { spirituality: 4, stress: 5, stamina: -4 },
        addTags: ["做过符号之梦"],
        addClues: [
          {
            id: "dream_route",
            title: "梦中的地下通道",
            text: "你记住了梦中的路线，墙上的符号与东区墙角那个几乎一模一样，尽头有一扇铁门。",
          },
        ],
      },
      {
        label: "强迫自己醒来",
        result: "你在梦里掐了自己一下，猛地惊醒。路线模糊了，但你知道那不是普通的梦。",
        effects: { spirituality: 2, stress: 3 },
        addTags: ["做过符号之梦"],
      },
    ],
  },
  {
    id: "first_beyonder",
    title: "初涉非凡",
    locations: ["east", "market", "station"],
    requiresClues: ["dream_route"],
    onceTag: "初涉非凡",
    text: "一个穿深色大衣的陌生人拦住你，准确说出了你最近追查的事。他说可以“帮”你，只需要你替他做一点小事。",
    chance: 70,
    weight: 5,
    minDay: 25,
    choices: [
      {
        label: "答应帮忙",
        result: "你接下委托：把一封信塞进东区某扇铁门下的缝隙。你第一次真正触碰到了非凡世界的门槛。",
        effects: { mysticism: 5, spirituality: 4, corruption: 1, stress: 6 },
        exposureChange: 12,
        addTags: ["初涉非凡"],
        addClues: [
          {
            id: "beyonder_first_contact",
            title: "第一位非凡者",
            text: "有人知道你在追查异常，并提出用委托交换帮助。非凡世界确实存在。",
          },
        ],
      },
      {
        label: "婉言拒绝",
        result: "你退后一步拒绝了他。陌生人并不生气，只是笑着说：你会再来的。",
        effects: { spirituality: 1, stress: 3 },
        addTags: ["初涉非凡"],
      },
    ],
  },
];

const initialState = {
  schemaVersion: 20,
  day: 1,
  month: 1,
  year: 1348,
  daysLived: 0,
  character: {
    name: "埃文·莫里斯",
    age: 17,
    family: "下层中产",
    socialClass: "普通市民",
    trait: "谨慎",
  },
  stats: {
    health: 80,
    stamina: 70,
    intelligence: 55,
    charisma: 50,
    money: 120,
    stress: 20,
    mysticism: 0,
    spirituality: 5,
    corruption: 0,
  },
  careerId: "student",
  locationId: "north",
  finance: {
    workDaysThisMonth: 0,
    monthsSurvived: 0,
    rentPaidThisMonth: 0,
    monthlyFlags: {},
  },
  contacts: structuredClone(contactTemplates),
  locationReputation: {
    north: 0,
    market: 0,
    church: 0,
    east: 0,
    station: 0,
  },
  investigation: {
    exposure: 0,
    warnings: 0,
    cooldown: 0,
  },
  life: {
    nutrition: 70,
    sleep: 70,
    comfort: 50,
    fatigue: 20,
  },
  skills: {
    literacy: 0,
    profession: 0,
    social: 0,
    streetwise: 0,
  },
  world: {
    tickCount: 0,
    economyPressure: 0,
    cityTension: 0,
    eventGraph: {
      completedNodes: [],
    },
    locations: {
      north: { activity: 0 },
      market: { activity: 0 },
      church: { activity: 0 },
      east: { activity: 0 },
      station: { activity: 0 },
    },
    arcs: {
      abnormalDisappearance: {
        node: "unnoticed",
        history: [],
      },
    },
  },
  ui: {
    mapOpen: false,
  },
  tags: [],
  clues: [],
  deductions: [],
  log: [],
  pendingEvent: null,
};

let state = loadState();

const ids = [
  "health",
  "stamina",
  "intelligence",
  "charisma",
  "money",
  "stress",
  "mysticism",
  "spirituality",
  "corruption",
];

const cappedStatIds = ids.filter((id) => id !== "money");

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", () => takeAction(button.dataset.action));
});

document.querySelectorAll("[data-career]").forEach((button) => {
  button.addEventListener("click", () => changeCareer(button.dataset.career));
});

document.getElementById("autoDay").addEventListener("click", () => {
  if (state.pendingEvent) {
    resolveEvent(0);
    return;
  }
  takeAction(pickAutoAction());
});

document.getElementById("autoMonth").addEventListener("click", () => {
  for (let index = 0; index < 30; index += 1) {
    if (state.pendingEvent) {
      resolveEvent(0, false);
    }
    takeAction(pickAutoAction(), false);
  }
  render();
});

document.getElementById("newLife").addEventListener("click", () => {
  state = createRandomState();
  saveState();
  render();
});

document.getElementById("resetGame").addEventListener("click", () => {
  state = createDefaultState();
  saveState();
  render();
});

document.getElementById("toggleMap").addEventListener("click", () => {
  state.ui.mapOpen = !state.ui.mapOpen;
  saveState();
  render();
});

render();

function takeAction(actionId, shouldRender = true) {
  if (state.pendingEvent) {
    if (shouldRender) {
      render();
    }
    return;
  }

  if (actionId === "investigate" && getInvestigationCooldown() > 0) {
    if (shouldRender) {
      render();
    }
    return;
  }

  const action = actions[actionId];
  const effects = getActionEffects(actionId, action);
  applyEffects(effects);
  applyActionReputation(actionId);
  const lifeText = applyDailyLife(actionId);

  let text = `${action.summary} ${lifeText}`;
  if (actionId === "investigate") {
    text = `${text} ${runInvestigation()}`;
  }
  if (actionId === "deduce") {
    text = `${text} ${runDeduction()}`;
  }
  const event = rollEvent();
  if (event) {
    state.pendingEvent = { ...event, happenedAt: formatDate() };
    text = `${text} ${event.text}`;
  }

  addEntry(formatDate(), `${action.name}：${text}`);
  advanceDay();
  saveState();

  if (shouldRender) {
    render();
  }
}

function createDefaultState() {
  const newState = structuredClone(initialState);
  newState.log = [
    {
      date: "第五纪 1348年1月1日",
      text: "你来到廷根，人生还没有显露出任何神秘的裂缝。",
    },
  ];
  return newState;
}

function createRandomState() {
  const background = pick(backgrounds);
  const name = `${pick(namePool.given)}·${pick(namePool.family)}`;
  const newState = structuredClone(initialState);
  newState.character = {
    name,
    age: randomBetween(background.age[0], background.age[1]),
    family: background.family,
    socialClass: background.socialClass,
    trait: background.trait,
  };
  newState.careerId = background.careerId;
  newState.locationId = background.locationId;
  newState.contacts = structuredClone(contactTemplates);
  updateContactSchedules(newState);
  newState.tags = [...background.tags];
  applyEffectsToState(newState, background.stats);
  newState.log = [
    {
      date: "第五纪 1348年1月1日",
      text: `新人生：${name}，${newState.character.age}岁，${background.family}。${background.intro}`,
    },
  ];
  return newState;
}

function resolveEvent(choiceIndex, shouldRender = true) {
  const event = state.pendingEvent;
  if (!event) {
    return;
  }

  const choice = event.choices[choiceIndex];
  applyEffects(choice.effects || {});
  changeLife(choice.lifeEffects || {});
  applyExposureChange(choice.exposureChange || 0);
  applyTrustEffects(choice.trustEffects || {});
  applyLocationReputationEffects(choice.locationReputationEffects || {});
  if (choice.rentPayment) {
    state.finance.rentPaidThisMonth += choice.rentPayment;
  }
  if (event.monthlyFlag) {
    state.finance.monthlyFlags[event.monthlyFlag] = true;
  }
  if (event.onceTag) {
    addTag(event.onceTag);
  }
  (choice.addTags || []).forEach(addTag);
  (choice.addClues || []).forEach(addClue);
  completeEventGraphNode(event.id);
  updateStoryArcs();
  state.pendingEvent = null;
  addEntry(event.happenedAt || formatDate(), `${event.title}：${choice.result}`);
  saveState();

  if (shouldRender) {
    render();
  }
}

function changeCareer(careerId) {
  if (!careers[careerId] || state.pendingEvent || state.careerId === careerId) {
    render();
    return;
  }

  const career = careers[careerId];
  state.careerId = careerId;
  state.finance.workDaysThisMonth = 0;
  state.finance.rentPaidThisMonth = 0;
  applyEffects({ stress: 4 });
  addTag(`成为${career.name}`);
  addEntry(formatDate(), `职业变化：你开始以“${career.name}”的身份安排生活。${career.description}`);
  saveState();
  render();
}

function travelTo(locationId) {
  if (!locations[locationId] || state.pendingEvent || state.locationId === locationId) {
    render();
    return;
  }

  const location = locations[locationId];
  const previous = getLocation();
  const career = getCareer();
  state.locationId = locationId;
  state.ui.mapOpen = false;
  changeLocationReputation(locationId, 1);
  applyEffects({
    money: -(location.travelCost + career.dailyCost),
    stamina: -location.travelStamina,
    stress: locationId === "church" ? -1 : 1,
  });
  changeLife({
    nutrition: state.stats.money <= 0 ? -3 : -1,
    sleep: -2,
    fatigue: location.travelStamina,
    comfort: locationId === "church" ? 1 : 0,
  });
  applyLifePressure();

  let text = `你从${previous.name}来到${location.name}。${location.description}`;
  const event = rollEvent();
  if (event) {
    state.pendingEvent = { ...event, happenedAt: formatDate() };
    text = `${text} ${event.text}`;
  }

  addEntry(
    formatDate(),
    `移动：${text}`,
  );
  advanceDay();
  saveState();
  render();
}

function rollEvent() {
  const candidates = events.filter((event) => {
    return canEventTriggerAt(event, state.locationId);
  });
  const weighted = candidates.flatMap((event) => Array(event.weight || 1).fill(event));
  const event = weighted[Math.floor(Math.random() * weighted.length)];
  if (!event) {
    return null;
  }
  return Math.random() * 100 <= event.chance ? event : null;
}

function canEventTriggerAt(event, locationId) {
  const graphNode = getEventGraphNode(event.id);
  if (graphNode && !canTriggerEventGraphNode(graphNode)) {
    return false;
  }
  if (event.minDay !== undefined && state.daysLived < event.minDay) {
    return false;
  }
  if (event.locations && !event.locations.includes(locationId)) {
    return false;
  }
  if (event.requiresClues && !event.requiresClues.every(hasClue)) {
    return false;
  }
  if (event.requiresAnyClue && !event.requiresAnyClue.some(hasClue)) {
    return false;
  }
  if (event.requiresTags && !event.requiresTags.every((tag) => state.tags.includes(tag))) {
    return false;
  }
  if (event.requiresDeductions && !event.requiresDeductions.every(hasDeduction)) {
    return false;
  }
  if (event.requiresContacts && !hasRequiredContacts(event.requiresContacts)) {
    return false;
  }
  if (
    event.minLocationReputation !== undefined &&
    (state.locationReputation[locationId] || 0) < event.minLocationReputation
  ) {
    return false;
  }
  if (
    event.minInvestigationExposure !== undefined &&
    getInvestigationExposure() < event.minInvestigationExposure
  ) {
    return false;
  }
  if (event.onceTag && state.tags.includes(event.onceTag)) {
    return false;
  }
  if (event.monthlyFlag && state.finance.monthlyFlags[event.monthlyFlag]) {
    return false;
  }
  return true;
}

function applyEffects(effects) {
  Object.entries(effects).forEach(([key, value]) => {
    state.stats[key] += value;
  });

  clampStats(state);
}

function applyEffectsToState(targetState, effects) {
  Object.entries(effects).forEach(([key, value]) => {
    targetState.stats[key] += value;
  });
  clampStats(targetState);
}

function clampStats(targetState) {
  cappedStatIds.forEach((key) => {
    targetState.stats[key] = Math.max(0, Math.min(100, targetState.stats[key]));
  });
  targetState.stats.money = Math.max(0, targetState.stats.money);
}

function getActionEffects(actionId, action) {
  const career = getCareer();
  const effects = { ...action.effects };

  if (actionId === "work") {
    state.finance.workDaysThisMonth += 1;
    effects.money = (effects.money || 0) + career.workIncome;
    const professionBuffer = Math.floor(state.skills.profession / 20);
    effects.stress = (effects.stress || 0) + Math.max(2, career.workStress - professionBuffer);
  }

  if (actionId === "study" && career.studyBonus) {
    effects.intelligence = (effects.intelligence || 0) + career.studyBonus;
  }

  if (actionId === "study") {
    effects.intelligence = (effects.intelligence || 0) + Math.floor(state.skills.literacy / 25);
  }

  if (actionId === "investigate") {
    effects.money = (effects.money || 0) - 4;
  }

  effects.money = (effects.money || 0) - career.dailyCost;
  return effects;
}

function runInvestigation() {
  const candidates = investigations.filter((investigation) => {
    const contact = state.contacts[investigation.contactId];
    if (!contact || getContactLocation(contact) !== state.locationId) {
      return false;
    }
    if (contact.trust < investigation.minTrust) {
      return false;
    }
    if (investigation.requiresClues && !investigation.requiresClues.every(hasClue)) {
      return false;
    }
    if (investigation.requiresAnyClue && !investigation.requiresAnyClue.some(hasClue)) {
      return false;
    }
    if (
      investigation.requiresDeductions &&
      !investigation.requiresDeductions.every(hasDeduction)
    ) {
      return false;
    }
    return !hasClue(investigation.id);
  });

  if (candidates.length === 0) {
    improveLocalContacts(1);
    const riskText = applyInvestigationRisk({ baseRisk: 4, success: false });
    setInvestigationCooldown(2);
    return `你问了一圈，却只得到一些模糊闲话。至少你和附近的人稍微熟了一点。${riskText}`;
  }

  const investigation = pick(candidates);
  applyEffects(investigation.effects || {});
  changeTrust(investigation.contactId, investigation.trustChange || 0);
  changeLocationReputation(state.locationId, 2);
  (investigation.addClues || []).forEach(addClue);
  const riskText = applyInvestigationRisk({ baseRisk: investigation.risk || 8, success: true });
  setInvestigationCooldown(getInvestigationExposure() >= 24 ? 3 : 2);
  return `${investigation.result}${riskText}`;
}

function runDeduction() {
  const rule = deductionRules.find((candidate) => canApplyDeduction(candidate));
  if (!rule) {
    improveLocalContacts(1);
    return "你反复翻看记录，却还差关键一环。现在下结论只会把自己带偏。";
  }

  addDeduction(rule);
  applyEffects(rule.effects || {});
  (rule.addTags || []).forEach(addTag);
  return rule.text;
}

function canApplyDeduction(rule) {
  if (hasDeduction(rule.id)) {
    return false;
  }
  if (rule.requiresAll && !rule.requiresAll.every(hasClue)) {
    return false;
  }
  if (rule.requiresAny && !rule.requiresAny.some((group) => group.every(hasClue))) {
    return false;
  }
  return true;
}

function pickAutoAction() {
  if (state.stats.health < 45 || state.stats.stamina < 35) {
    return "rest";
  }
  if (state.stats.money < 60) {
    return "work";
  }
  if (state.stats.stress > 70) {
    return "social";
  }
  const pool = ["study", "work", "rest", "social", "wander"];
  return pool[Math.floor(Math.random() * pool.length)];
}

function advanceDay() {
  state.daysLived += 1;
  state.day += 1;
  worldTick();
  if (state.day > 30) {
    state.day = 1;
    state.month += 1;
    settleMonth();
  }
  if (state.month > 12) {
    state.month = 1;
    state.year += 1;
    advanceAge();
  }
}

function advanceAge() {
  state.character.age += 1;
  addTag(`${state.character.age}岁`);
  addEntry(
    formatDate(),
    `新年：时间进入 ${state.year} 年，${state.character.name} 又长了一岁。`,
  );
}

function worldTick() {
  state.world.tickCount += 1;
  reduceInvestigationCooldown();
  updateNpcLives(state);
  tickEconomy();
  tickLocations();
  updateStoryArcs();
}

function updateContactSchedules(targetState) {
  updateNpcLives(targetState);
}

function updateNpcLives(targetState) {
  Object.values(targetState.contacts).forEach((contact) => {
    if (contact.routine && contact.routine.length > 0) {
      const routine = contact.routine[targetState.daysLived % contact.routine.length];
      contact.currentLocationId = routine.locationId;
      contact.currentActivity = routine.activity;
      return;
    }
    if (!contact.schedule || contact.schedule.length === 0) {
      contact.currentLocationId = contact.locationId;
      contact.currentActivity = contact.currentActivity || "维持日常生活";
      return;
    }
    contact.currentLocationId = contact.schedule[targetState.daysLived % contact.schedule.length];
    contact.currentActivity = contact.currentActivity || "维持日常生活";
  });
}

function tickEconomy() {
  const pressure = state.stats.money < getCareer().rent ? 1 : -1;
  state.world.economyPressure = Math.max(0, Math.min(100, state.world.economyPressure + pressure));
}

function tickLocations() {
  Object.entries(state.world.locations).forEach(([locationId, locationState]) => {
    const nearbyContacts = Object.values(state.contacts).filter(
      (contact) => getContactLocation(contact) === locationId,
    ).length;
    const baseline = locations[locationId]?.risk || 0;
    const drift = nearbyContacts + Math.floor(baseline / 10) - 1;
    locationState.activity = Math.max(0, Math.min(100, locationState.activity + drift));
  });
  state.world.cityTension = Math.max(
    0,
    Math.min(
      100,
      Math.floor(
        getInvestigationExposure() * 0.45 +
          state.world.economyPressure * 0.25 +
          state.stats.stress * 0.15 +
          (state.world.locations.east?.activity || 0) * 0.15,
      ),
    ),
  );
}

function updateStoryArcs(targetState = state) {
  const arc = targetState.world.arcs.abnormalDisappearance;
  const previous = arc.node;
  let next = "unnoticed";
  const clueIds = new Set((targetState.clues || []).map((clue) => clue.id));
  const deductionIds = new Set((targetState.deductions || []).map((deduction) => deduction.id));
  const tags = targetState.tags || [];

  if (clueIds.has("missing_notice")) {
    next = "rumor";
  }
  if (clueIds.has("newspaper_overlap") || clueIds.has("old_button") || clueIds.has("wall_symbol")) {
    next = "clue_found";
  }
  if (clueIds.has("old_hat_man") || clueIds.has("avoid_east_night")) {
    next = "npc_contact";
  }
  if (deductionIds.has("east_case_pattern")) {
    next = "decision";
  }
  if (tags.includes("向教会举报")) {
    next = "reported";
  }
  if (tags.includes("隐瞒失踪线索")) {
    next = "concealed";
  }
  if (tags.includes("决定追到底")) {
    next = "committed";
  }
  if (clueIds.has("church_coin") || clueIds.has("deep_night_route")) {
    next = "coin";
  }
  if (tags.includes("做过符号之梦")) {
    next = "dream";
  }
  if (tags.includes("初涉非凡")) {
    next = "first_contact";
  }

  if (next !== previous) {
    arc.node = next;
    arc.history.push({ day: targetState.daysLived, node: next });
    arc.history = arc.history.slice(-20);
  }
}

function getEventGraphNode(eventId) {
  return eventGraphNodes.find((node) => node.eventId === eventId);
}

function canTriggerEventGraphNode(node) {
  const completed = state.world.eventGraph.completedNodes || [];
  if (!node.repeatable && completed.includes(node.id)) {
    return false;
  }
  if (node.afterNodes && !node.afterNodes.every((nodeId) => completed.includes(nodeId))) {
    return false;
  }
  return true;
}

function completeEventGraphNode(eventId) {
  const node = getEventGraphNode(eventId);
  if (!node || node.repeatable) {
    return;
  }
  const completed = state.world.eventGraph.completedNodes;
  if (!completed.includes(node.id)) {
    completed.push(node.id);
  }
}

function getEventGraphSummary() {
  const ordinaryTotal = eventGraphNodes.filter((node) => node.type === "ordinary").length;
  const abnormalTotal = eventGraphNodes.filter((node) => node.type === "abnormal").length;
  const mysticTotal = eventGraphNodes.filter((node) => node.type === "mystic").length;
  const completed = new Set(state.world.eventGraph.completedNodes || []);
  return {
    ordinaryTotal,
    abnormalTotal,
    mysticTotal,
    ordinaryDone: eventGraphNodes.filter(
      (node) => node.type === "ordinary" && completed.has(node.id),
    ).length,
    abnormalDone: eventGraphNodes.filter(
      (node) => node.type === "abnormal" && completed.has(node.id),
    ).length,
    mysticDone: eventGraphNodes.filter(
      (node) => node.type === "mystic" && completed.has(node.id),
    ).length,
  };
}

function getNpcScheduleSummary() {
  const contacts = Object.values(state.contacts);
  return {
    total: contacts.length,
    scheduled: contacts.filter((contact) => contact.routine && contact.routine.length >= 7).length,
  };
}

function getContactsAtLocation(locationId) {
  return Object.values(state.contacts).filter((contact) => getContactLocation(contact) === locationId);
}

function getAvailableEventCount(locationId) {
  return events.filter((event) => canEventTriggerAt(event, locationId)).length;
}

function settleMonth() {
  const career = getCareer();
  let salaryPaid = career.salary;
  const remainingRent = Math.max(0, career.rent - state.finance.rentPaidThisMonth);
  let summary = `月度结算：`;

  if (career.requiredWorkDays > 0) {
    const ratio = Math.min(1, state.finance.workDaysThisMonth / career.requiredWorkDays);
    salaryPaid = Math.floor(career.salary * ratio);
    summary += ` 本月工作 ${state.finance.workDaysThisMonth}/${career.requiredWorkDays} 天，获得薪水 ${salaryPaid} 镑。`;
  } else if (career.salary > 0) {
    summary += ` 获得薪水 ${salaryPaid} 镑。`;
  } else {
    summary += " 你没有固定月薪，只能依靠平日收入。";
  }

  if (remainingRent > 0) {
    summary += ` 你支付了剩余 ${remainingRent} 镑房租。`;
  } else {
    summary += " 本月房租已经提前处理完毕。";
  }

  applyEffects({ money: salaryPaid - remainingRent });

  if (state.stats.money <= 0) {
    applyEffects({ stress: 12, health: -3 });
    changeLife({ nutrition: -10, comfort: -8 });
    addTag("财务紧张");
    summary += " 钱包见底，生活压力开始压到身体上。";
  } else if (state.stats.money < career.rent) {
    applyEffects({ stress: 6 });
    changeLife({ comfort: -4 });
    addTag("房租压力");
    summary += " 剩余的钱不多，你已经开始担心下个月。";
  } else {
    applyEffects({ stress: -3 });
    changeLife({ comfort: 3 });
    summary += " 至少这个月暂时撑过去了。";
  }

  const lifeStatus = getLifeStatus();
  if (lifeStatus.label === "稳定") {
    addTag("生活稳定");
  }
  if (lifeStatus.label === "失衡") {
    addTag("生活失衡");
  }
  summary += ` 本月生活状态：${lifeStatus.label}。`;

  state.finance.monthsSurvived += 1;
  state.finance.workDaysThisMonth = 0;
  state.finance.rentPaidThisMonth = 0;
  state.finance.monthlyFlags = {};
  applyExposureChange(-6);
  addEntry(formatDate(), summary);
}

function addEntry(date, text) {
  state.log.push({ date, text });
  state.log = state.log.slice(-80);
}

function addTag(tag) {
  if (!state.tags.includes(tag)) {
    state.tags.push(tag);
  }
}

function addClue(clue) {
  if (!state.clues.some((item) => item.id === clue.id)) {
    state.clues.push(clue);
  }
}

function addDeduction(deduction) {
  if (!state.deductions.some((item) => item.id === deduction.id)) {
    state.deductions.push({
      id: deduction.id,
      title: deduction.title,
      text: deduction.text,
    });
  }
}

function hasClue(clueId) {
  return state.clues.some((clue) => clue.id === clueId);
}

function hasDeduction(deductionId) {
  return state.deductions.some((deduction) => deduction.id === deductionId);
}

function changeTrust(contactId, amount) {
  const contact = state.contacts[contactId];
  if (!contact) {
    return;
  }
  contact.trust = Math.max(0, Math.min(100, contact.trust + amount));
}

function improveLocalContacts(amount) {
  Object.entries(state.contacts).forEach(([contactId, contact]) => {
    if (getContactLocation(contact) === state.locationId) {
      changeTrust(contactId, amount);
    }
  });
}

function changeLocationReputation(locationId, amount) {
  const current = state.locationReputation[locationId] || 0;
  state.locationReputation[locationId] = Math.max(0, Math.min(100, current + amount));
}

function applyActionReputation(actionId) {
  const amountByAction = {
    social: 2,
    wander: 1,
    work: 1,
    investigate: 1,
    deduce: 0,
    study: 0,
    rest: 0,
  };
  changeLocationReputation(state.locationId, amountByAction[actionId] || 0);
}

function applyDailyLife(actionId) {
  const hungryPenalty = state.stats.money <= 0 ? -5 : -1;
  const changesByAction = {
    study: { life: { nutrition: hungryPenalty, sleep: -5, fatigue: 8 }, skills: { literacy: 3 } },
    work: { life: { nutrition: hungryPenalty, sleep: -6, fatigue: 16, comfort: -1 }, skills: { profession: 3 } },
    rest: { life: { nutrition: 1, sleep: 14, fatigue: -20, comfort: 3 }, skills: {} },
    social: { life: { nutrition: -2, sleep: -2, fatigue: 4, comfort: 3 }, skills: { social: 3 } },
    wander: { life: { nutrition: hungryPenalty, sleep: -2, fatigue: 7, comfort: 1 }, skills: { streetwise: 2 } },
    investigate: { life: { nutrition: hungryPenalty, sleep: -4, fatigue: 10, comfort: -2 }, skills: { streetwise: 1 } },
    deduce: { life: { nutrition: hungryPenalty, sleep: -5, fatigue: 9 }, skills: { literacy: 1 } },
  };
  const changes = changesByAction[actionId] || { life: {}, skills: {} };
  changeLife(changes.life);
  changeSkills(changes.skills);
  return applyLifePressure();
}

function changeLife(changes) {
  Object.entries(changes).forEach(([key, amount]) => {
    state.life[key] = Math.max(0, Math.min(100, (state.life[key] || 0) + amount));
  });
}

function changeSkills(changes) {
  Object.entries(changes).forEach(([key, amount]) => {
    state.skills[key] = Math.max(0, Math.min(100, (state.skills[key] || 0) + amount));
  });
}

function applyLifePressure() {
  const effects = {};
  const notes = [];

  if (state.life.nutrition < 30) {
    effects.health = (effects.health || 0) - 2;
    effects.stamina = (effects.stamina || 0) - 3;
    notes.push("饥饿让身体变沉。");
  }
  if (state.life.sleep < 30) {
    effects.stress = (effects.stress || 0) + 3;
    effects.stamina = (effects.stamina || 0) - 2;
    state.life.fatigue = Math.min(100, state.life.fatigue + 3);
    notes.push("睡眠不足让你难以集中。");
  }
  if (state.life.fatigue > 75) {
    effects.health = (effects.health || 0) - 2;
    effects.stress = (effects.stress || 0) + 4;
    notes.push("长期疲劳开始拖垮状态。");
  }
  if (state.life.comfort < 25) {
    effects.stress = (effects.stress || 0) + 2;
    notes.push("生活缺少安稳感。");
  }
  if (state.life.nutrition > 65 && state.life.sleep > 65 && state.life.fatigue < 45) {
    effects.health = (effects.health || 0) + 1;
    effects.stamina = (effects.stamina || 0) + 2;
  }

  applyEffects(effects);
  return notes.length > 0 ? notes.join("") : getLifeStatus().dailyText;
}

function getLifeStatus() {
  const average =
    (state.life.nutrition + state.life.sleep + state.life.comfort + (100 - state.life.fatigue)) /
    4;
  if (average >= 72) {
    return { label: "稳定", dailyText: "生活节奏还算稳定。" };
  }
  if (average >= 52) {
    return { label: "尚可", dailyText: "日子过得紧，但还能维持。" };
  }
  if (average >= 34) {
    return { label: "吃紧", dailyText: "生活状态正在变差。" };
  }
  return { label: "失衡", dailyText: "生活已经明显失衡。" };
}

function applyInvestigationRisk({ baseRisk, success }) {
  const location = getLocation();
  const familiar = state.locationReputation[state.locationId] || 0;
  const cluePressure = Math.min(18, state.clues.length * 2 + state.deductions.length * 3);
  const spiritualBuffer = Math.floor(state.stats.spirituality / 12);
  const riskScore = Math.max(
    3,
    baseRisk + location.risk + cluePressure - Math.floor(familiar / 3) - spiritualBuffer,
  );

  if (Math.random() * 100 > riskScore) {
    return success ? " 这次打听没有引起明显注意。" : "";
  }

  const exposureGain = success ? randomBetween(3, 7) : randomBetween(1, 4);
  applyExposureChange(exposureGain);
  state.investigation.warnings += 1;

  if (riskScore >= 34 || getInvestigationExposure() >= 24) {
    applyEffects({ stress: 5, stamina: -3 });
    addTag("追查引来注视");
    return " 你感觉有人记住了你的问题，背后像多了一道视线。";
  }

  applyEffects({ stress: 2 });
  return " 这个问题让谈话短暂冷了下来，你意识到自己问得有些深了。";
}

function applyExposureChange(amount) {
  state.investigation.exposure = Math.max(0, Math.min(100, getInvestigationExposure() + amount));
}

function getInvestigationExposure() {
  return state.investigation?.exposure || 0;
}

function setInvestigationCooldown(days) {
  state.investigation.cooldown = Math.max(getInvestigationCooldown(), days);
}

function reduceInvestigationCooldown() {
  state.investigation.cooldown = Math.max(0, getInvestigationCooldown() - 1);
}

function getInvestigationCooldown() {
  return state.investigation?.cooldown || 0;
}

function getRiskTier() {
  const exposure = getInvestigationExposure();
  if (exposure >= 45) {
    return { label: "暴露", className: "critical" };
  }
  if (exposure >= 25) {
    return { label: "危险", className: "danger" };
  }
  if (exposure >= 12) {
    return { label: "紧张", className: "warning" };
  }
  return { label: "平稳", className: "calm" };
}

function applyTrustEffects(trustEffects) {
  Object.entries(trustEffects).forEach(([contactId, amount]) => {
    changeTrust(contactId, amount);
  });
}

function applyLocationReputationEffects(reputationEffects) {
  Object.entries(reputationEffects).forEach(([locationId, amount]) => {
    changeLocationReputation(locationId, amount);
  });
}

function hasRequiredContacts(requiredContacts) {
  return Object.entries(requiredContacts).every(([contactId, minTrust]) => {
    const contact = state.contacts[contactId];
    return contact && contact.trust >= minTrust;
  });
}

function pick(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function randomBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function formatDate() {
  return `第五纪 ${state.year}年${state.month}月${state.day}日`;
}

function render() {
  renderCharacter();
  ids.forEach((id) => {
    document.getElementById(id).textContent = state.stats[id];
  });
  document.getElementById("date").textContent = formatDate();
  document.getElementById("dayCount").textContent = `第 ${state.daysLived + 1} 天`;
  renderCareer();
  renderLife();
  renderLocation();
  renderMap();
  renderWorld();

  const log = document.getElementById("storyLog");
  log.innerHTML = state.log
    .map(
      (entry) => `
        <article class="entry">
          <p class="entry-date">${entry.date}</p>
          <p class="entry-text">${entry.text}</p>
        </article>
      `,
    )
    .join("");
  log.scrollTop = log.scrollHeight;

  renderTags();
  renderClues();
  renderDeductions();
  renderContacts();
  renderPendingEvent();
}

function renderCharacter() {
  document.getElementById("characterName").textContent = state.character.name;
  document.getElementById("characterAge").textContent = state.character.age;
  document.getElementById("familyName").textContent = state.character.family;
  document.getElementById("className").textContent = state.character.socialClass;
  document.getElementById("traitName").textContent = state.character.trait;
}

function renderLocation() {
  const location = getLocation();
  const riskTier = getRiskTier();
  const riskLabel = document.getElementById("investigationRiskLabel");
  document.getElementById("locationName").textContent = location.name;
  document.getElementById("currentLocation").textContent = location.name;
  document.getElementById("locationReputation").textContent =
    state.locationReputation[state.locationId] || 0;
  document.getElementById("investigationExposure").textContent = getInvestigationExposure();
  riskLabel.textContent = riskTier.label;
  riskLabel.className = `risk-badge ${riskTier.className}`;
  document.getElementById("locationRisk").textContent = location.risk;
  document.getElementById("investigationCooldown").textContent = getInvestigationCooldown();
  document.getElementById("locationDescription").textContent = location.description;

  document.querySelectorAll("[data-location]").forEach((button) => {
    button.classList.toggle("active", button.dataset.location === state.locationId);
    button.disabled = Boolean(state.pendingEvent);
  });
}

function renderMap() {
  const cityMap = document.querySelector(".city-map");
  const mapNodes = document.getElementById("mapNodes");
  const currentContacts = getContactsAtLocation(state.locationId);
  const currentEventCount = getAvailableEventCount(state.locationId);
  const currentLocation = getLocation();
  document.getElementById(
    "mapSummary",
  ).textContent = `${currentLocation.name} · NPC ${currentContacts.length} · 事件 ${currentEventCount}`;
  document.getElementById("toggleMap").textContent = state.ui.mapOpen ? "收起地图" : "打开地图";
  cityMap.classList.toggle("expanded", state.ui.mapOpen);

  if (!state.ui.mapOpen) {
    mapNodes.innerHTML = "";
    return;
  }

  mapNodes.innerHTML = Object.entries(locations)
    .map(([locationId, location]) => {
      const active = locationId === state.locationId ? " active" : "";
      const blocked = state.pendingEvent ? " disabled" : "";
      const contactsHere = getContactsAtLocation(locationId);
      const eventCount = getAvailableEventCount(locationId);
      const activity = state.world.locations[locationId]?.activity || 0;
      const npcNames = contactsHere
        .slice(0, 3)
        .map((contact) => contact.name)
        .join("、");
      const npcText =
        contactsHere.length === 0
          ? "暂无熟人"
          : contactsHere.length > 3
            ? `${npcNames} 等 ${contactsHere.length} 人`
            : npcNames;
      return `
        <button class="map-node ${locationId}${active}${blocked}" data-location="${locationId}">
          <strong>${location.name}</strong>
          <span>${location.tags.join(" / ")}</span>
          <small>NPC ${contactsHere.length} · 事件 ${eventCount}</small>
          <small>危险 ${location.risk} · 活跃 ${activity}</small>
          <em>${npcText}</em>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll("[data-location]").forEach((button) => {
    button.addEventListener("click", () => travelTo(button.dataset.location));
    button.disabled = Boolean(state.pendingEvent);
  });
}

function renderWorld() {
  const arc = state.world.arcs.abnormalDisappearance;
  const graphSummary = getEventGraphSummary();
  const npcSummary = getNpcScheduleSummary();
  document.getElementById("cityTension").textContent = state.world.cityTension;
  document.getElementById("economyPressure").textContent = state.world.economyPressure;
  document.getElementById("disappearanceArc").textContent =
    storyArcLabels[arc.node] || storyArcLabels.unnoticed;
  document.getElementById(
    "ordinaryGraphCount",
  ).textContent = `${graphSummary.ordinaryDone}/${graphSummary.ordinaryTotal}`;
  document.getElementById(
    "abnormalGraphCount",
  ).textContent = `${graphSummary.abnormalDone}/${graphSummary.abnormalTotal}`;
  document.getElementById("mysticGraphCount").textContent =
    `${graphSummary.mysticDone}/${graphSummary.mysticTotal}`;
  document.getElementById("npcScheduleCount").textContent =
    `${npcSummary.scheduled}/${npcSummary.total}`;
}

function renderCareer() {
  const career = getCareer();
  document.getElementById("careerName").textContent = career.name;
  document.getElementById("salary").textContent = career.salary;
  document.getElementById("rent").textContent = career.rent;
  document.getElementById("rentPaid").textContent = Math.min(
    state.finance.rentPaidThisMonth,
    career.rent,
  );
  document.getElementById("dailyCost").textContent = career.dailyCost;
  document.getElementById("monthlyBalance").textContent = getExpectedMonthlyBalance(career);
  document.getElementById("workDays").textContent =
    career.requiredWorkDays > 0
      ? `${state.finance.workDaysThisMonth}/${career.requiredWorkDays}`
      : `${state.finance.workDaysThisMonth}`;

  document.querySelectorAll("[data-career]").forEach((button) => {
    button.classList.toggle("active", button.dataset.career === state.careerId);
    button.disabled = Boolean(state.pendingEvent);
  });
}

function renderLife() {
  const lifeStatus = getLifeStatus();
  document.getElementById("nutrition").textContent = state.life.nutrition;
  document.getElementById("sleep").textContent = state.life.sleep;
  document.getElementById("comfort").textContent = state.life.comfort;
  document.getElementById("fatigue").textContent = state.life.fatigue;
  document.getElementById("lifeStatus").textContent = lifeStatus.label;
  document.getElementById("literacySkill").textContent = state.skills.literacy;
  document.getElementById("professionSkill").textContent = state.skills.profession;
  document.getElementById("socialSkill").textContent = state.skills.social;
  document.getElementById("streetwiseSkill").textContent = state.skills.streetwise;
}

function getExpectedMonthlyBalance(career) {
  const livingCost = career.dailyCost * 30 + career.rent;
  if (career.salary > 0) {
    return career.salary - livingCost;
  }
  return career.workIncome * 18 - livingCost;
}

function renderTags() {
  const tags = document.getElementById("tags");
  if (state.tags.length === 0) {
    tags.innerHTML = `<span class="empty-tag">暂无</span>`;
    return;
  }
  tags.innerHTML = state.tags.map((tag) => `<span>${tag}</span>`).join("");
}

function renderClues() {
  const clues = document.getElementById("clues");
  if (state.clues.length === 0) {
    clues.innerHTML = `<span class="empty-tag">暂无</span>`;
    return;
  }
  clues.innerHTML = state.clues
    .map(
      (clue) => `
        <article class="clue">
          <strong>${clue.title}</strong>
          <p>${clue.text}</p>
        </article>
      `,
    )
    .join("");
}

function renderDeductions() {
  const deductions = document.getElementById("deductions");
  if (state.deductions.length === 0) {
    deductions.innerHTML = `<span class="empty-tag">暂无</span>`;
    return;
  }
  deductions.innerHTML = state.deductions
    .map(
      (deduction) => `
        <article class="deduction">
          <strong>${deduction.title}</strong>
          <p>${deduction.text}</p>
        </article>
      `,
    )
    .join("");
}

function renderContacts() {
  const contacts = document.getElementById("contacts");
  const entries = Object.entries(state.contacts);
  if (entries.length === 0) {
    contacts.innerHTML = `<span class="empty-tag">暂无</span>`;
    return;
  }

  contacts.innerHTML = entries
    .map(([contactId, contact]) => {
      const contactLocationId = getContactLocation(contact);
      const location = locations[contactLocationId] || locations.north;
      const nearby = contactLocationId === state.locationId ? " nearby" : "";
      return `
        <article class="contact${nearby}">
          <div>
            <strong>${contact.name}</strong>
            <span>${contact.role} · ${location.name}</span>
            <span>${contact.currentActivity || "维持日常生活"}</span>
          </div>
          <b>${contact.trust}</b>
        </article>
      `;
    })
    .join("");
}

function renderPendingEvent() {
  const panel = document.getElementById("eventPanel");
  const buttons = document.querySelectorAll("[data-action]");
  const event = state.pendingEvent;

  buttons.forEach((button) => {
    const isCoolingInvestigation =
      button.dataset.action === "investigate" && getInvestigationCooldown() > 0;
    button.disabled = Boolean(event) || isCoolingInvestigation;
    button.classList.toggle("cooling", isCoolingInvestigation);
  });

  if (!event) {
    panel.classList.add("hidden");
    return;
  }

  panel.classList.remove("hidden");
  document.getElementById("eventTitle").textContent = event.title;
  document.getElementById("eventText").textContent = event.text;
  document.getElementById("eventChoices").innerHTML = event.choices
    .map(
      (choice, index) =>
        `<button class="choice-button" data-choice="${index}">${choice.label}</button>`,
    )
    .join("");

  document.querySelectorAll("[data-choice]").forEach((button) => {
    button.addEventListener("click", () => resolveEvent(Number(button.dataset.choice)));
  });
}

function saveState() {
  localStorage.setItem("mysteries-life-v20", JSON.stringify(state));
}

function loadState() {
  const saved =
    localStorage.getItem("mysteries-life-v20") ||
    localStorage.getItem("mysteries-life-v19") ||
    localStorage.getItem("mysteries-life-v18") ||
    localStorage.getItem("mysteries-life-v17") ||
    localStorage.getItem("mysteries-life-v16") ||
    localStorage.getItem("mysteries-life-v15") ||
    localStorage.getItem("mysteries-life-v14") ||
    localStorage.getItem("mysteries-life-v13") ||
    localStorage.getItem("mysteries-life-v12") ||
    localStorage.getItem("mysteries-life-v11") ||
    localStorage.getItem("mysteries-life-v10") ||
    localStorage.getItem("mysteries-life-v09") ||
    localStorage.getItem("mysteries-life-v08") ||
    localStorage.getItem("mysteries-life-v07") ||
    localStorage.getItem("mysteries-life-v06") ||
    localStorage.getItem("mysteries-life-v05") ||
    localStorage.getItem("mysteries-life-v04") ||
    localStorage.getItem("mysteries-life-v03") ||
    localStorage.getItem("mysteries-life-v02") ||
    localStorage.getItem("mysteries-life-v01");
  if (!saved) {
    return createDefaultState();
  }
  try {
    return normalizeState(JSON.parse(saved));
  } catch {
    return structuredClone(initialState);
  }
}

function normalizeState(savedState) {
  const savedVersion = savedState.schemaVersion || 5;
  const savedLog = savedState.log || [];
  const contacts = mergeContacts(savedState.contacts || {});
  const normalized = {
    ...structuredClone(initialState),
    ...savedState,
    schemaVersion: initialState.schemaVersion,
    stats: {
      ...initialState.stats,
      ...(savedState.stats || {}),
    },
    character: {
      ...initialState.character,
      ...(savedState.character || {}),
    },
    tags: savedState.tags || [],
    clues: savedState.clues || [],
    deductions: savedState.deductions || [],
    log: savedVersion < 6 ? [...savedLog].reverse() : savedLog,
    pendingEvent: savedState.pendingEvent || null,
    careerId: savedState.careerId || "student",
    locationId: savedState.locationId || "north",
    finance: {
      ...initialState.finance,
      ...(savedState.finance || {}),
    },
    contacts,
    locationReputation: {
      ...initialState.locationReputation,
      ...(savedState.locationReputation || {}),
    },
    investigation: {
      ...initialState.investigation,
      ...(savedState.investigation || {}),
    },
    life: {
      ...initialState.life,
      ...(savedState.life || {}),
    },
    skills: {
      ...initialState.skills,
      ...(savedState.skills || {}),
    },
    world: mergeWorld(savedState.world || {}),
    ui: {
      ...initialState.ui,
      ...(savedState.ui || {}),
    },
  };
  updateContactSchedules(normalized);
  updateStoryArcs(normalized);
  return normalized;
}

function getCareer() {
  return careers[state.careerId] || careers.student;
}

function getLocation() {
  return locations[state.locationId] || locations.north;
}

function getContactLocation(contact) {
  return contact.currentLocationId || contact.locationId;
}

function mergeContacts(savedContacts) {
  const merged = structuredClone(contactTemplates);
  Object.entries(savedContacts).forEach(([contactId, savedContact]) => {
    merged[contactId] = {
      ...(merged[contactId] || {}),
      ...savedContact,
      schedule: savedContact.schedule || merged[contactId]?.schedule || [],
      routine: savedContact.routine || merged[contactId]?.routine || [],
      currentLocationId:
        savedContact.currentLocationId ||
        merged[contactId]?.currentLocationId ||
        savedContact.locationId,
      currentActivity:
        savedContact.currentActivity ||
        merged[contactId]?.currentActivity ||
        "维持日常生活",
    };
  });
  return merged;
}

function mergeWorld(savedWorld) {
  const base = structuredClone(initialState.world);
  return {
    ...base,
    ...savedWorld,
    locations: {
      ...base.locations,
      ...(savedWorld.locations || {}),
    },
    eventGraph: {
      ...base.eventGraph,
      ...(savedWorld.eventGraph || {}),
      completedNodes: savedWorld.eventGraph?.completedNodes || [],
    },
    arcs: {
      ...base.arcs,
      ...(savedWorld.arcs || {}),
      abnormalDisappearance: {
        ...base.arcs.abnormalDisappearance,
        ...(savedWorld.arcs?.abnormalDisappearance || {}),
        history: savedWorld.arcs?.abnormalDisappearance?.history || [],
      },
    },
  };
}
