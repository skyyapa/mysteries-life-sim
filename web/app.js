// 版本戳：browser title 展示当前加载版本（防缓存旧版误判）
const APP_VERSION = "v31";
try {
  document.title = `人生模拟器 ${APP_VERSION}`;
} catch (e) {
  /* noop */
}

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
      { id: "ordinary_rain", eventId: "rainy_cold", label: "冷雨", repeatable: true },
      { id: "ordinary_book", eventId: "cheap_book", label: "旧书摊", repeatable: true },
      { id: "ordinary_bell", eventId: "church_bell", label: "钟声", repeatable: true },
      { id: "ordinary_rent", eventId: "landlord_pressure", label: "房租压力", repeatable: true },
      { id: "ordinary_pickpocket", eventId: "market_pickpocket", label: "市场扒手", repeatable: true },
      { id: "ordinary_overtime", eventId: "work_overtime", label: "加班要求", repeatable: true },
      { id: "ordinary_exam", eventId: "study_exam", label: "课堂测验", repeatable: true },
      { id: "ordinary_neighbor_soup", eventId: "neighbor_soup", label: "邻居热汤", repeatable: true },
      { id: "ordinary_market_price", eventId: "market_price_rise", label: "市场涨价", repeatable: true },
      { id: "ordinary_home_leak", eventId: "home_leak", label: "屋顶漏水", repeatable: true },
      { id: "ordinary_winter_coal", eventId: "winter_coal", label: "冬季煤价", repeatable: true },
      { id: "ordinary_spring_mud", eventId: "spring_mud", label: "开春泥路", repeatable: true },
      { id: "ordinary_summer_heat", eventId: "summer_heat", label: "盛夏酷暑", repeatable: true },
      { id: "ordinary_autumn_harvest", eventId: "autumn_harvest", label: "秋日集市", repeatable: true },
      { id: "career_student_prize", eventId: "career_student_prize", label: "奖学金", repeatable: true },
      { id: "career_apprentice_test", eventId: "career_apprentice_test", label: "师傅考校", repeatable: true },
      { id: "career_clerk_audit", eventId: "career_clerk_audit", label: "月底查账", repeatable: true },
      { id: "career_temp_short", eventId: "career_temp_short", label: "工钱缩水", repeatable: true },
      { id: "ordinary_illness", eventId: "illness", label: "染上风寒", repeatable: true },
      { id: "ordinary_broken_boots", eventId: "broken_boots", label: "靴子开线", repeatable: true },
      { id: "ordinary_bank_counter", eventId: "bank_counter", label: "银行柜台", repeatable: true },
      { id: "ordinary_friend_errand", eventId: "friend_private_errand", label: "朋友的私事" },
      { id: "ordinary_confession", eventId: "confession_event", label: "深夜倾吐" },
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
  hiddenCurrent: {
    title: "廷根的暗流",
    type: "mystic",
    nodes: [
      {
        id: "mainline_errand",
        eventId: "second_errand",
        label: "第二委托",
        afterNodes: ["mystic_beyonder"],
      },
      {
        id: "mainline_church",
        eventId: "church_voice",
        label: "教会的声音",
        afterNodes: ["mainline_errand"],
      },
      {
        id: "mainline_loss",
        eventId: "losing_control",
        label: "失控前兆",
        afterNodes: ["mainline_church"],
      },
      {
        id: "mainline_truth",
        eventId: "truth_choice",
        label: "真相抉择",
        afterNodes: ["mainline_loss"],
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
  divination: {
    name: "占卜",
    requiresPathway: "占卜家",
    summary: "你摆弄着茶梗与烛焰，半梦半醒间仿佛看见了一些若隐若现的纹路。",
    effects: { spirituality: -6, stress: 6, mysticism: 1 },
    addTag: "占卜过",
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
  save: {
    name: "存钱",
    summary: "你走进北区的储蓄银行，把 10 镑存进柜台。利息虽少，但总好过放在口袋里。",
    effects: { stamina: -3 },
  },
  withdraw: {
    name: "取钱",
    summary: "你到银行取出 10 镑现金应急。存款少了一截，但手头宽裕了。",
    effects: { stamina: -3 },
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
    chance: 24,
    weight: 3,
    minDay: 5,
    maxDay: 120,
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
    maxDay: 60,
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
    cooldownDays: 30,
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
    onceTag: "发现报纸重叠",
    text: "你在报纸边角看到一则短讯：有人在东区附近失踪，警方只说还在调查。",
    chance: 24,
    weight: 3,
    minDay: 6,
    maxDay: 90,
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
    onceTag: "被教士提醒",
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
    onceTag: "被跟踪经历",
    text: "你经过那条小巷时，身后的脚步声忽然和你的步伐保持了同样节奏。",
    chance: 30,
    weight: 3,
    minDay: 10,
    maxDay: 150,
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
  {
    id: "winter_coal",
    title: "煤价上涨",
    locations: ["market", "north"],
    season: "winter",
    minDay: 40,
    cooldownDays: 25,
    text: "入冬后煤价涨了一截。卖煤的老汉说，今年运河结冰早，运不进来。",
    chance: 20,
    weight: 3,
    choices: [
      {
        label: "多囤一点煤",
        result: "你咬牙多买了一袋煤。钱包薄了，但冬天不用在夜里被冻醒。",
        effects: { money: -8, comfort: 4, stress: -2 },
      },
      {
        label: "省着烧",
        result: "你决定把炭火调到最小。屋里冷了些，但账面撑住了。",
        effects: { money: 3, comfort: -3, stress: 2 },
      },
    ],
  },
  {
    id: "spring_mud",
    title: "开春泥路",
    locations: ["market", "east", "station"],
    season: "spring",
    minDay: 90,
    cooldownDays: 30,
    text: "开春雪水化开，廷根的街道变成泥河。马车陷在坑里，车夫大声咒骂着。",
    chance: 16,
    weight: 2,
    choices: [
      {
        label: "绕远路",
        result: "你多走了一刻钟绕开泥坑，靴子保住了。",
        effects: { stamina: -3, stress: -1 },
      },
      {
        label: "帮忙推车",
        result: "你帮着推了一把，车夫塞给你几个便士，说你还算可靠。",
        effects: { stamina: -6, money: 2, charisma: 1 },
      },
    ],
  },
  {
    id: "summer_heat",
    title: "盛夏酷暑",
    locations: ["north", "east"],
    season: "summer",
    minDay: 150,
    cooldownDays: 30,
    text: "夏日的廷根闷热难耐。傍晚的街道晒了一天，空气里全是尘土和散热的气味。",
    chance: 18,
    weight: 3,
    choices: [
      {
        label: "买一杯凉饮",
        result: "街角摊子的凉饮很贵，但确实让脑子清醒了一些。",
        effects: { money: -3, stress: -3, health: 1 },
      },
      {
        label: "忍一忍",
        result: "你省下了钱，但到家时已经头晕眼花。",
        effects: { money: 2, health: -2, stamina: -2 },
      },
    ],
  },
  {
    id: "autumn_harvest",
    title: "秋日集市",
    locations: ["market"],
    season: "autumn",
    minDay: 240,
    cooldownDays: 30,
    text: "秋天的集市堆满了苹果、面包和熏鱼。摊贩们难得露出笑脸。",
    chance: 16,
    weight: 3,
    choices: [
      {
        label: "买点应季食物",
        result: "你买了几颗苹果和一袋面粉。物美价廉，心情也跟着好了。",
        effects: { money: -4, health: 2, stress: -2 },
      },
      {
        label: "只是逛逛",
        result: "你在人群里走了一圈，闻着食物的香气，没花一分钱。",
        effects: { stress: -1, charisma: 1 },
      },
    ],
  },
  {
    id: "career_student_prize",
    title: "奖学金机会",
    locations: ["north"],
    jobs: ["文法学校学生"],
    minDay: 30,
    cooldownDays: 60,
    text: "学校宣布，学年末成绩优异者可以获得一份奖学金，足够抵掉几个月的开销。",
    chance: 16,
    weight: 2,
    choices: [
      {
        label: "报名参赛",
        result: "你把课余时间都压在备考上。这是一场赌博，但奖品值得一试。",
        effects: { intelligence: 3, stress: 6, stamina: -4 },
        addTags: ["争取奖学金"],
      },
      {
        label: "量力而行",
        result: "你决定保住平时的节奏。奖学金很好，但不是唯一的路。",
        effects: { stress: -2 },
        addTags: ["放弃奖学金"],
      },
    ],
  },
  {
    id: "career_apprentice_test",
    title: "师傅考校",
    locations: ["market", "north"],
    jobs: ["店铺学徒"],
    minDay: 30,
    cooldownDays: 60,
    text: "师傅突然说要考校你最近的功夫。他板着脸，但你知道这是机会。",
    chance: 16,
    weight: 2,
    choices: [
      {
        label: "全力以赴",
        result: "你把自己学到的东西全使了出来。师傅没说话，但嘴角动了动。",
        effects: { intelligence: 2, stress: 5, charisma: 1 },
        addTags: ["师傅认可"],
      },
      {
        label: "求稳",
        result: "你只做了最有把握的部分。不难看，但也不出彩。",
        effects: { stress: -1 },
        addTags: ["应对考试"],
      },
    ],
  },
  {
    id: "career_clerk_audit",
    title: "月底查账",
    locations: ["north"],
    jobs: ["事务所文员"],
    minDay: 30,
    cooldownDays: 60,
    text: "事务所月底要查账。主管把一摞厚账本推到你面前，语气很轻：别出错。",
    chance: 16,
    weight: 2,
    choices: [
      {
        label: "连夜核对",
        result: "你查了三遍，挑出两处小错。主管罕见地对你点了点头。",
        effects: { intelligence: 2, stress: 7, stamina: -6 },
        addTags: ["账目无误"],
      },
      {
        label: "按时下班",
        result: "你照常下班。身体轻松，但你知道明天可能不好过。",
        effects: { stress: -1 },
        addTags: ["账目平常"],
      },
    ],
  },
  {
    id: "career_temp_short",
    title: "工钱缩水",
    locations: ["market", "east"],
    jobs: ["临时工"],
    minDay: 30,
    cooldownDays: 60,
    text: "工头发工钱时少给了几先令。他说这是“扣下的一笔管理费”。",
    chance: 16,
    weight: 2,
    choices: [
      {
        label: "当面质问",
        result: "你当着众人的面把数目点给他看。工头冷笑，但还是补上了差额。",
        effects: { money: 5, stress: 6, charisma: 1 },
        addTags: ["据理力争"],
      },
      {
        label: "忍下这口气",
        result: "你接过钱走开了。几先令不值得丢掉这份活计。",
        effects: { money: -4, stress: 2 },
        addTags: ["忍气吞声"],
      },
    ],
  },
  {
    id: "illness",
    title: "染上风寒",
    locations: ["north", "east", "market"],
    minDay: 10,
    cooldownDays: 40,
    text: "冷风钻进领口，你头重脚轻地熬了半日，晚上开始发低烧。诊所的医生把听诊器贴在你胸口。",
    chance: 12,
    weight: 2,
    choices: [
      {
        label: "花钱看病",
        result: "你付了诊费和药费。肉痛，但至少夜里烧退了。",
        effects: { money: -8, health: 10, stress: -2 },
      },
      {
        label: "硬扛过去",
        result: "你捂紧被子硬扛。省下了钱，第二天却差点起不来床。",
        effects: { health: -5, stamina: -6, stress: 3 },
      },
    ],
  },
  {
    id: "broken_boots",
    title: "靴子开线",
    locations: ["market", "north"],
    minDay: 15,
    cooldownDays: 35,
    text: "你低头才发现靴底已经磨穿，冷气直往脚心钻。修鞋摊的老头报价不高，但也不便宜。",
    chance: 14,
    weight: 2,
    choices: [
      {
        label: "修补",
        result: "老头手法利落，半小时后靴子又结实了。",
        effects: { money: -5, comfort: 2, stress: -1 },
      },
      {
        label: "凑合穿",
        result: "你决定再撑一阵。走路时能感觉脚底隔着袜子贴到石板。",
        effects: { money: 3, health: -2, comfort: -3 },
      },
    ],
  },
  {
    id: "bank_counter",
    title: "银行柜台",
    locations: ["north"],
    minDay: 5,
    cooldownDays: 20,
    text: "储蓄银行柜台前排着不长不短的队。牌子上写着：存款月息 2%。排队的人都在盘算着什么。",
    chance: 16,
    weight: 1,
    choices: [
      {
        label: "存 10 镑",
        result: "你把 10 镑存了进去。柜员在存折上写下一行字，动作很慢，像是在纪念什么。",
        effects: { stress: -1 },
        special: "deposit",
      },
      {
        label: "只看看",
        result: "你读完了告示，记住了利率，转身离开了银行。",
        effects: { intelligence: 1 },
      },
    ],
  },
  {
    id: "friend_private_errand",
    title: "朋友的私事",
    locations: ["north", "market", "east"],
    requiresContacts: { neighbor: 40 },
    onceTag: "帮朋友办过私事",
    text: "莎伦太太犹豫了很久，托你替她给城另一头的亲戚带一封信。她说这封信不该走邮局。",
    chance: 18,
    weight: 2,
    minDay: 8,
    choices: [
      {
        label: "答应捎带",
        result: "你把信送到。亲戚一家很感激，回赠了你几个自家烘的馅饼。",
        effects: { charisma: 2, stress: -2, money: 1 },
        trustEffects: { neighbor: 5 },
        addTags: ["帮朋友办过私事"],
      },
      {
        label: "婉言推辞",
        result: "你说自己最近忙不过来。她没说什么，但你知道这份信任打了折扣。",
        effects: { stress: 1 },
        trustEffects: { neighbor: -3 },
      },
    ],
  },
  {
    id: "confession_event",
    title: "深夜里的话",
    locations: ["north", "market", "church"],
    requiresContacts: { neighbor: 70 },
    onceTag: "向挚友倾吐过真心",
    text: "夜已经深了。莎伦太太坐在你对面，忽然问你：最近是不是有什么事，一个人扛着很累吧？",
    chance: 22,
    weight: 2,
    minDay: 20,
    choices: [
      {
        label: "说出实情",
        result: "你把最近追查的事挑能说的说了。她听完没有追问，只说你白天记得好好吃饭。",
        effects: { stress: -8, spirituality: 1 },
        trustEffects: { neighbor: 6 },
        addTags: ["向挚友倾吐过真心"],
      },
      {
        label: "笑着说没事",
        result: "你摇头说一切都好。她的眼神说明她并不信，但她没有拆穿。",
        effects: { stress: 1 },
        trustEffects: { neighbor: 1 },
      },
    ],
  },
  {
    id: "second_errand",
    title: "第二件委托",
    locations: ["east", "market", "station"],
    requiresTags: ["初涉非凡"],
    minDay: 30,
    onceTag: "完成第二件委托",
    text: "深衣人再次出现，交给你第二件委托：今夜子时，把一封信放在教堂地窖铁门口。他说“这次不要看信的内容”。",
    chance: 35,
    weight: 4,
    choices: [
      {
        label: "照做",
        result: "你把信放在铁门口，转身离开时听见门内有人低声念着什么。你开始做奇怪的梦。",
        effects: { corruption: 3, madness: 5, stress: 5 },
        addTags: ["完成第二件委托"],
        addClues: [
          {
            id: "second_errand_clue",
            title: "教堂地窖的交接",
            text: "深衣人通过你向教堂地窖递过一封信，门内有人在夜里念诵。",
          },
        ],
      },
      {
        label: "拒绝",
        result: "你拒绝了。深衣人没有勉强，但你看得出他记住了这次拒绝。",
        effects: { stress: 2 },
        addTags: ["拒绝深衣人"],
      },
    ],
  },
  {
    id: "church_voice",
    title: "教会的声音",
    locations: ["church"],
    requiresClues: ["second_errand_clue", "church_coin"],
    minDay: 36,
    onceTag: "与教士深谈",
    text: "奥尔森教士找到你，语气比往常更沉：他说他注意到你“最近睡得不好”。他在等你开口。",
    chance: 38,
    weight: 4,
    choices: [
      {
        label: "坦白一切",
        result: "你把深衣人的委托和盘托出。教士沉默良久，说：你做的没错，但这条路越走，越难回头。",
        effects: { stress: -6, spirituality: 3, madness: -5 },
        trustEffects: { priest: 6 },
        addTags: ["与教士深谈", "向教士坦白"],
        addClues: [
          {
            id: "priest_accepts",
            title: "教士的接纳",
            text: "奥尔森教士知道了深衣人的存在，愿意在必要时庇护你。",
          },
        ],
      },
      {
        label: "遮掩过去",
        result: "你说只是没睡好。教士没有追问，但你感觉那道目光在你身上停得太久。",
        effects: { stress: 3, madness: 2 },
        addTags: ["与教士深谈"],
      },
    ],
  },
  {
    id: "losing_control",
    title: "失控前兆",
    locations: ["north", "east"],
    requiresClues: ["second_errand_clue"],
    minDay: 42,
    minMadness: 40,
    onceTag: "度过失控之夜",
    text: "午夜你惊醒，发现自己正站在窗边，手里握着那把教堂旧硬币。你不记得自己是怎么走到这里的。",
    chance: 45,
    weight: 5,
    choices: [
      {
        label: "去教堂求助",
        result: "你连夜敲开教堂的门。教士为你守了一夜，可怕的东西没有再来。",
        effects: { madness: -15, spirituality: 4, stress: -5 },
        trustEffects: { priest: 4 },
        addTags: ["度过失控之夜"],
        addClues: [
          {
            id: "survived_night",
            title: "度过失控之夜",
            text: "你在教士的看护下度过了一夜，但你知道自己离失控并不远。",
          },
        ],
      },
      {
        label: "独自硬扛",
        result: "你握住旧硬币坐到天亮。什么也没发生，但你知道自己撑不过第二次。",
        effects: { madness: 5, stress: 8, stamina: -6 },
        addTags: ["独自硬扛一夜"],
      },
    ],
  },
  {
    id: "truth_choice",
    title: "真相抉择",
    locations: ["east", "north"],
    requiresClues: ["second_errand_clue"],
    minDay: 48,
    onceTag: "做出非凡抉择",
    text: "你终于拼出深衣人的身份——他不是普通掮客，某个非凡组织正借廷根的地窖做交换。他递来一张名片，说：加入，或者离开，都随你。",
    chance: 50,
    weight: 6,
    choices: [
      {
        label: "加入组织",
        result: "你接过名片。他说会在合适的时机教你怎么“用双手握住命运”。",
        effects: { corruption: 5, madness: 8, mysticism: 3 },
        addTags: ["做出非凡抉择", "加入神秘组织"],
        addClues: [
          {
            id: "joined_org",
            title: "神秘组织的邀请",
            text: "深衣人代表某个组织接纳了你，承诺教你接触非凡的方法。",
          },
        ],
      },
      {
        label: "投向教会",
        result: "你把名片交给教士。教士收下后说：你会成为教会的线人，但从此你的每一步都会有人看着。",
        effects: { spirituality: 5, stress: 4 },
        trustEffects: { priest: 6 },
        addTags: ["做出非凡抉择", "成为教会线人"],
        addClues: [
          {
            id: "church_ally",
            title: "教会的线人",
            text: "你选择站在黑夜教会一边，从此知晓一些不该知晓的事。",
          },
        ],
      },
      {
        label: "抽身退回",
        result: "你推开名片，说你要做普通人。他笑了：你以为现在还来得及吗？",
        effects: { stress: 6, spirituality: 2 },
        addTags: ["做出非凡抉择", "试图抽身"],
        addClues: [
          {
            id: "step_back",
            title: "试图回到普通生活",
            text: "你想切断与非凡的一切联系，但有些东西一旦接触就不会放过你。",
          },
        ],
      },
    ],
  },
  {
    id: "pathway_choice",
    title: "途径：属于你的路",
    text: "真相抉择之后，属于你的那条路开始显现。你隐约感到，自己与某些古老的东西有了说不清的联系。",
    chance: 60,
    weight: 6,
    minDay: 52,
    requiresTags: ["加入神秘组织"],
    onceTag: "选定途径",
    choices: [
      {
        label: "成为占卜家",
        result: "你对某些征兆格外敏感——茶梗、烛焰、镜面。你选择以占卜为路。",
        effects: { _pathway: "占卜家", spirituality: 5, mysticism: 3 },
        addTags: ["选定途径"],
      },
      {
        label: "成为观众",
        result: "你选择观察。看人、看场合、看那些隐藏的意图。",
        effects: { _pathway: "观众", charisma: 4, spirituality: 2 },
        addTags: ["选定途径"],
      },
      {
        label: "成为不眠者",
        result: "从今夜起，你与夜晚为伴。黑暗不再是威胁。",
        effects: { _pathway: "不眠者", stamina: 4, spirituality: 3 },
        addTags: ["选定途径"],
      },
    ],
  },
  {
    id: "seq_advance_seer",
    title: "晋升：小丑魔药",
    text: "深衣人交给你一支细颈玻璃瓶——小丑魔药。灵性在瓶壁内流转，隐约传来戏谑的笑声。",
    chance: 34,
    weight: 5,
    minDay: 62,
    requiresTags: ["途径：占卜家"],
    onceTag: "占卜家晋升",
    choices: [
      {
        label: "饮下魔药",
        result: "你仰头饮下。",
        effects: { _potion: 8 },
        addTags: ["占卜家晋升"],
      },
      {
        label: "再等等",
        result: "你把瓶子收进怀中。有些玩笑，还不是时候。",
        effects: { stress: -2 },
        addTags: ["占卜家晋升"],
      },
    ],
  },
  {
    id: "seq_advance_reader",
    title: "晋升：读心者魔药",
    text: "剧院后台，一个戴单片眼镜的女人递给你一杯闻不出味道的酒——读心者魔药。她说：喝了它，你就能听见人心里的话。",
    chance: 34,
    weight: 5,
    minDay: 62,
    requiresTags: ["途径：观众", "看破谎言"],
    onceTag: "观众晋升",
    choices: [
      {
        label: "饮下魔药",
        result: "酒入喉后，周围的低语忽然清晰成词。",
        effects: { _potion: 8 },
        addTags: ["观众晋升"],
      },
      {
        label: "婉拒",
        result: "她笑而不语，收回了酒杯。有些东西，推辞过一次就不会再来。",
        effects: { stress: -2 },
        addTags: ["观众晋升"],
      },
    ],
  },
  {
    id: "seq_advance_insomn",
    title: "晋升：午夜诗人魔药",
    text: "午夜，老守夜人将一杯黑色的液体推到你面前——午夜诗人魔药。它会让你的夜晚比白天更清醒。",
    chance: 34,
    weight: 5,
    minDay: 62,
    requiresTags: ["途径：不眠者", "不眠者夜巡"],
    onceTag: "不眠者晋升",
    choices: [
      {
        label: "饮下魔药",
        result: "黑暗在你眼中褪去，巷子里每一粒尘埃都清晰可见。",
        effects: { _potion: 8 },
        addTags: ["不眠者晋升"],
      },
      {
        label: "把杯子推回去",
        result: "老守夜人沉默片刻：那便再守一段夜吧。",
        effects: { stress: -2 },
        addTags: ["不眠者晋升"],
      },
    ],
  },
  {
    id: "festival_wake",
    title: "万象节",
    text: "三月伊始，冰冻的运河解了封。万象节让整座廷根从蛰伏中醒来——街上挂满褪色的旧彩带，人人都像重新活了一遍。",
    chance: 70,
    weight: 5,
    calendar: { month: 3, day: 1 },
    cooldownDays: 360,
    choices: [
      {
        label: "加入巡游",
        result: "你跟着人群走了三个街区，笑得像忘了这年冬天的糟心事。",
        effects: { health: 3, stress: -6 },
        addTags: ["过万象节"],
      },
      {
        label: "趁热闹摆摊卖旧物",
        result: "节日里什么都卖得动。你清掉了积灰的杂物，换回几枚银币。",
        effects: { money: 8, stamina: -4 },
        addTags: ["过万象节"],
      },
    ],
  },
  {
    id: "festival_longnight",
    title: "长夜节",
    text: "长夜节到了。黑夜教堂的钟声从黄昏响到黎明，信徒举着烛灯沿街巡游，沉默得像一场巨大的梦。",
    chance: 75,
    weight: 6,
    calendar: { month: 7, day: 30 },
    cooldownDays: 360,
    choices: [
      {
        label: "加入巡游与守夜",
        result: "一整夜，你在烛火与颂声里没有合眼。天亮时分，你觉得自己离某个不可言说的东西近了一线。",
        effects: { spirituality: 4, mysticism: 2, stress: 4, stamina: -8 },
        addTags: ["守过长夜"],
      },
      {
        label: "远远看着，不去打扰",
        result: "你站在街角看完了整场巡游。有些仪式不属于你，但这座城市因为它们而存在。",
        effects: { stress: -2, spirituality: 1 },
        addTags: ["守过长夜"],
      },
    ],
  },
  {
    id: "festival_harvest",
    title: "丰收感恩日",
    text: "丰收感恩日，市场外支起了长桌。面包、苹果和熏鱼堆得像小山，街坊们破天荒地互相道谢。",
    chance: 70,
    weight: 5,
    calendar: { month: 9, day: 21 },
    cooldownDays: 360,
    choices: [
      {
        label: "与街坊共宴",
        result: "你认识了几个新面孔，也慰劳了老交情。这顿饭吃得值。",
        effects: { charisma: 3, money: -5, stress: -4 },
        trustEffects: { neighbor: 3, newsboy: 3 },
        addTags: ["共赴丰收宴"],
      },
      {
        label: "帮忙卸货换工钱",
        result: "你帮着把一筐筐苹果搬进仓库，主人家给了不错的工钱。",
        effects: { money: 12, stamina: -8 },
        addTags: ["共赴丰收宴"],
      },
    ],
  },
  {
    id: "festival_year_end",
    title: "岁末之夜",
    text: "岁末之夜，全城点亮红灯笼。教堂的炉火彻夜不熄，老人们说：这一夜许下的愿，来年会回来找你。",
    chance: 75,
    weight: 6,
    calendar: { month: 12, day: 25 },
    cooldownDays: 360,
    choices: [
      {
        label: "在教堂许愿并守夜",
        result: "你跪在长椅前许了一个愿。炉火噼啪作响，你感到久违的安宁——以及一丝被人注视的错觉。",
        effects: { spirituality: 3, stress: -8 },
        addTags: ["岁末许愿"],
      },
      {
        label: "买一份热红酒独酌",
        result: "热红酒的香气里，你想起这一年走过的路。有些人已经不在了，但你还在。",
        effects: { money: -4, stress: -5, madness: -3 },
        addTags: ["岁末许愿"],
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
    madness: 0,
  },
  careerId: "student",
  locationId: "north",
  finance: {
    workDaysThisMonth: 0,
    monthsSurvived: 0,
    rentPaidThisMonth: 0,
    monthlyFlags: {},
    savings: 0,
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
    eventLastTriggered: {},
    expiredTraced: {},
    organizations: {
      黑夜教会: { attention: 0 },
      暗流组织: { activity: 0 },
    },
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
    focusedContactId: null,
    autoLife: true,
    autoPlay: false,
    lastSummaryYear: null,
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

document.querySelectorAll("[data-career]").forEach((button) => {
  button.addEventListener("click", () => changeCareer(button.dataset.career));
});

document.getElementById("autoDay").addEventListener("click", () => {
  if (state.pendingEvent) {
    render();
    return; // 事件等待玩家选择
  }
  // v0.27 点击一下 = 过一天：一天按早/午/晚三个时段生活，遇到事件停下交给玩家
  liveOneFullDay();
  saveState();
  render();
  if (state.pendingEvent) {
    showSaveToast("遇到事件——轮到你做选择了");
  }
});

document.getElementById("newLife").addEventListener("click", () => {
  if (!confirm(`生成新人生将放弃当前人生（${formatDate()}，第 ${state.daysLived} 天）。\n确定要重新开始吗？`)) {
    return;
  }
  state = createRandomState();
  saveState();
  render();
});

document.getElementById("resetGame").addEventListener("click", () => {
  if (!confirm("重新开始将清除当前进度并恢复默认人生。确定吗？")) {
    return;
  }
  state = createDefaultState();
  saveState();
  render();
});

document.getElementById("toggleMap").addEventListener("click", () => {
  state.ui.mapOpen = !state.ui.mapOpen;
  saveState();
  render();
});

document.getElementById("summaryClose").addEventListener("click", () => {
  const panel = document.getElementById("summaryPanel");
  if (panel) {
    panel.classList.add("hidden");
  }
  state.ui.lastSummaryYear = state.year;
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
  advanceDayWithAction(actionId, shouldRender);
}

/**
 * v0.27 一天由早/午/晚三时段组成：执行动作但只在当天结束时推进日期。
 * 事件不中断当天：三时段照常过完，事件在当天结束后交给你抉择。
 */
function liveOneFullDay() {
  if (state.pendingEvent) {
    return;
  }
  const slotActions = pickDaySlots();
  const happened = [];
  for (const slot of slotActions) {
    const text = performActionOnce(slot.action, slot.label, false, true);
    if (text) {
      happened.push(text);
    }
  }
  // 三时段全部过完后再 roll 事件（不打断今天）
  const event = rollEvent();
  if (event) {
    state.pendingEvent = { ...event, happenedAt: formatDate() };
    happened.push(`晚间：${event.text}`);
  }
  // 只有那天真正过了才推进日期与月结算
  const day = advanceDayNoEvent();
  const logLines = happened.filter(Boolean);
  if (logLines.length > 0) {
    addEntry(formatDate(), logLines.join(" ").slice(0, 600));
  }
  saveState();
  render();
  return day;
}

/** 为今天的三时段挑选动作（上午重生存，午后重发展，晚上轻恢复，尽量不重复）。 */
function pickDaySlots() {
  const morning = pickAutoAction();
  const noon = pickNoonAction();
  const used = new Set([morning, noon]);
  const evening = pickEveningAction(used);
  return [
    { label: "早晨", action: morning },
    { label: "午后", action: noon },
    { label: "夜晚", action: evening },
  ];
}

function pickNoonAction() {
  // 午后：优先推进主线/调查，其次工作/社交
  if (state.clues.length >= 2 && state.stats.money >= 40 && getInvestigationCooldown() <= 0 && Math.random() < 0.55) {
    return "investigate";
  }
  if (state.clues.length >= 2 && state.deductions.length < 4 && Math.random() < 0.4) {
    return "deduce";
  }
  if (state.stats.money < 60) {
    return "work";
  }
  return pick(["work", "social", "wander", "study"]);
}

function pickEveningAction(used = new Set()) {
  const pathway = state.character?.pathway;
  if (pathway === "占卜家" && state.stats.spirituality >= 12 && state.stats.money >= 40 && Math.random() < 0.25 && !used.has("divination")) {
    return "divination";
  }
  if (state.stats.stress > 60 && !used.has("rest")) {
    return "rest";
  }
  if (state.stats.money >= 40 && state.finance.savings < 120 && Math.random() < 0.2 && !used.has("save")) {
    return "save";
  }
  const pool = ["rest", "social", "wander", "study"].filter((a) => !used.has(a));
  return pool.length > 0 ? pick(pool) : "rest";
}

/** 纯执行一次动作：applyEffects + 生活描述，不推进日期、不 roll 事件。
 * force=true：当天三时段内即使已有待处理事件也继续过完（事件在当天末尾再呈现）。 */
function performActionOnce(actionId, slotLabel, shouldRender, force = false) {
  if (state.pendingEvent && !force) {
    return "";
  }
  const action = actions[actionId];
  if (!action) {
    return "";
  }
  const effects = getActionEffects(actionId, action);
  applyEffects(effects);
  applyActionReputation(actionId);
  let text = `${action.summary}`;

  if (actionId === "investigate") {
    if (getInvestigationCooldown() > 0) {
      text = "线索还不清晰，你决定今天把调查搁下。";
    } else {
      const inv = runInvestigation();
      if (inv) {
        state.pendingEvent = undefined; // 调查结果作为事件即时呈现
        text = `${text} ${inv}`;
      } else {
        text = `${text} 但没问出什么新的。`;
      }
    }
  } else if (actionId === "deduce") {
    text = `${text} ${runDeduction()}`;
  } else if (actionId === "save") {
    const deposited = Math.min(10, state.stats.money);
    if (deposited > 0) {
      state.stats.money -= deposited;
      state.finance.savings += deposited;
    } else {
      text = "你走到银行门口，摸了摸空荡荡的口袋，只好转身回去。";
    }
  } else if (actionId === "withdraw") {
    const withdrawn = Math.min(10, state.finance.savings || 0);
    if (withdrawn > 0) {
      state.finance.savings -= withdrawn;
      state.stats.money += withdrawn;
    } else {
      text = "你的存款是零，银行柜员礼貌地请你让开后面的队伍。";
    }
  }
  return `${slotLabel}：${text}`;
}

/** 推进日期（无事件判定），返回是否跨月。 */
function advanceDayNoEvent() {
  state.daysLived += 1;
  state.day += 1;
  worldTick();
  let crossedMonth = false;
  if (state.day > 30) {
    state.day = 1;
    state.month += 1;
    settleMonth();
    crossedMonth = true;
  }
  if (state.month > 12) {
    state.month = 1;
    state.year += 1;
    advanceAge();
    state.ui.lastSummaryYear = null;
    showLifeSummary();
  }
  return crossedMonth;
}

/** 兼容旧调用：单动作一天（直接一次时段执行 + 推进日期）。 */
function advanceDayWithAction(actionId, shouldRender = true) {
  if (state.pendingEvent) {
    if (shouldRender) {
      render();
    }
    return;
  }
  const parts = [performActionOnce(actionId, "今日", false)];
  const event = rollEvent();
  if (event) {
    state.pendingEvent = { ...event, happenedAt: formatDate() };
    parts.push(`晚间：${event.text}`);
  }
  advanceDayNoEvent();
  const text = parts.filter(Boolean).join(" ");
  if (text) {
    addEntry(formatDate(), text.slice(0, 600));
  }
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

/** V0.30 Web 版魔药失控检定（镜像 Python mysticism.sequences.drink_potion）。
 * 诱因逐项累积 → 失控率；失控后三档后果（发狂/扭曲/死亡）。
 */
function drinkPotionWeb(targetSeq) {
  const c = state.character || {};
  const spirit = state.stats.spirituality ?? 0;
  const stress = state.stats.stress ?? 0;
  const mood = state.stats.mood ?? 50;
  const madness = state.stats.madness ?? 0;

  // 门槛/风险参数（与 sequences.py 对齐）
  const gate = targetSeq <= 8 ? 25 : 45;
  let risk = 0.06 + (targetSeq <= 8 ? 0.06 : 0); // 相性差基线 + 高序列污染
  const deficit = Math.max(0, gate - spirit);
  if (deficit > 0) {
    risk += Math.min(0.7, 0.45 * (deficit / gate) * 3); // 灵性外溢
  }
  if (stress > 60) risk += 0.12;
  if (mood < 25) risk += 0.1;
  if (madness > 60) risk += 0.15;
  if (madness >= 80) risk += 0.35;
  const tags = state.tags || [];
  if (tags.some((t) => ["精神污染", "接触高位格", "邪神呓语"].includes(t))) {
    risk += 0.08;
  }
  risk = Math.min(0.97, risk);

  // 失控 roll
  if (Math.random() >= risk) {
    // 平稳晋升
    const name = ({ 8: "小丑", 7: "魔术师" })[targetSeq] ||
      ({ 8: "读心者", 7: "心理医生" })[targetSeq] || "晋升者";
    return {
      sequence: targetSeq,
      text: `魔药在意识中沉定成新的形状，你成为「${name}」。`,
      effects: { spirituality: 4, madness: 10 },
      tags: [`序列：${name}`],
      dead: false,
    };
  }

  // 失控：三档后果（55:32:13）
  const roll = Math.random() * 100;
  if (roll < 13) {
    // S 精神死亡·身体崩溃
    return {
      text: "魔药的力量炸开了你意识的最深处——灵魂在震爆中湮灭，身体开始异变、崩解（失控·精神死亡）。",
      effects: { madness: 30, health: -50, stamina: -20 },
      tags: ["身体崩溃", "魔药反噬", "精神污染"],
      dead: true,
    };
  }
  if (roll < 45) {
    // A 人格被扭曲
    return {
      text: "魔药中那道古老意志压过了你——你清醒地感受着自己变得冷酷残忍，却再也找不回原来的自己（失控·人格扭曲）。晋升失败。",
      effects: { madness: 16, charisma: -6, stress: 6 },
      tags: ["人格被扭曲", "魔药反噬", "精神污染"],
      dead: false,
    };
  }
  // B 当场发狂
  return {
    text: "魔药入喉，你的精神当场崩断——你发疯般撕扯着一切近身之物（失控·发狂）。众人合力才将你制住，晋升失败。",
    effects: { madness: 14, stress: 12, stamina: -6 },
    tags: ["当场发狂", "魔药反噬", "灵性外溢"],
    dead: false,
  };
}

function resolveEvent(choiceIndex, shouldRender = true) {
  const event = state.pendingEvent;
  if (!event) {
    return;
  }

  const choice = event.choices[choiceIndex];
  let appliedText = choice.result;
  const effects = { ...(choice.effects || {}) };

  // V0.28/V0.30：途径选择（_pathway）→ 设途径 + 起始序列 9
  if (effects._pathway !== undefined) {
    state.character.pathway = effects._pathway;
    state.character.sequence = 9;
    addTag(`途径：${effects._pathway}`);
    addTag(`序列：${effects._pathway}`);
    delete effects._pathway;
  }

  // V0.30：魔药晋升（_potion）→ Web 版失控检定（复刻 Python drink_potion 语义）
  if (effects._potion !== undefined) {
    const potionResult = drinkPotionWeb(effects._potion);
    appliedText = potionResult.text;
    Object.assign(effects, potionResult.effects);
    delete effects._potion;
    if (potionResult.dead) {
      state.character.dead = true;
      state.character.deathReason = "失控：精神死亡，身体异变崩解";
      addTag("身体崩溃");
    }
    (potionResult.tags || []).forEach(addTag);
    if (potionResult.sequence) {
      state.character.sequence = potionResult.sequence;
    }
  }

  applyEffects(effects);
  changeLife(choice.lifeEffects || {});
  applyExposureChange(choice.exposureChange || 0);
  applyTrustEffects(choice.trustEffects || {});
  applyLocationReputationEffects(choice.locationReputationEffects || {});
  if (choice.special === "deposit") {
    // 银行事件：把效果里的现金支出转入存款
    const deposited = Math.min(10, state.stats.money);
    state.stats.money -= deposited;
    state.finance.savings += deposited;
  }
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
  markEventTriggered(event);
  updateStoryArcs();
  state.pendingEvent = null;
  addEntry(event.happenedAt || formatDate(), `${event.title}：${appliedText}`);
  // V0.30：失控死亡后存档并提示（专属终局提示，不弹年度总结）
  if (state.character.dead) {
    saveState();
    if (shouldRender) {
      render();
    }
    window.alert(`感染(精神死亡)·身体崩解——${state.character.name}在晋升中失控，灵魂在魔药的力量下湮灭。\n这段人生结束了。可「重新开始」或读档回溯。`);
    return;
  }
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
    return canEventTriggerAt(event, state.locationId) && !isEventOnCooldown(event);
  });
  const weighted = candidates.flatMap((event) => Array(event.weight || 1).fill(event));
  const event = weighted[Math.floor(Math.random() * weighted.length)];
  if (!event) {
    return null;
  }
  return Math.random() * 100 <= event.chance ? event : null;
}

function getSeason(month) {
  const m = month || state.month || 1;
  if (m === 12 || m === 1 || m === 2) return "winter";
  if (m >= 3 && m <= 5) return "spring";
  if (m >= 6 && m <= 8) return "summer";
  return "autumn";
}

function isEventOnCooldown(event) {
  if (!event.cooldownDays) {
    return false;
  }
  const last = (state.world.eventLastTriggered || {})[event.id];
  if (last === undefined) {
    return false;
  }
  return state.daysLived - last < event.cooldownDays;
}

function markEventTriggered(event) {
  if (!event.cooldownDays) {
    return;
  }
  if (!state.world.eventLastTriggered) {
    state.world.eventLastTriggered = {};
  }
  state.world.eventLastTriggered[event.id] = state.daysLived;
}

function canEventTriggerAt(event, locationId) {
  const graphNode = getEventGraphNode(event.id);
  if (graphNode && !canTriggerEventGraphNode(graphNode)) {
    return false;
  }
  if (event.minDay !== undefined && state.daysLived < event.minDay) {
    return false;
  }
  if (event.maxDay !== undefined && state.daysLived > event.maxDay) {
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
  if (event.season && getSeason(state.month) !== event.season) {
    return false;
  }
  if (event.months && !event.months.includes(state.month)) {
    return false;
  }
  // V0.31 节日：特定月日才可触发
  if (
    event.calendar &&
    !(event.calendar.month === (state.month || 1) && event.calendar.day === (state.day || 1))
  ) {
    return false;
  }
  if (event.jobs && !event.jobs.includes(getCareer().name)) {
    return false;
  }
  if (event.minMadness !== undefined && (state.stats.madness || 0) < event.minMadness) {
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

  // V0.23 途径加成
  const pathway = state.character?.pathway;
  if (action.requiresPathway && action.requiresPathway !== pathway) {
    // 途径专属行动校验：不满足则忽略该行动（调用方已避免，此处兜底）
    return { ...effects, blocked: true };
  }
  if (pathway === "观众" && actionId === "social") {
    effects.charisma = (effects.charisma || 0) + 3; // 洞察人心，社交更有效
  }
  if (pathway === "不眠者" && (actionId === "work" || actionId === "investigate")) {
    effects.stamina = (effects.stamina || 0) + 4; // 夜行耐力
  }
  if (actionId === "divination") {
    effects.mysticism = (effects.mysticism || 0) + 1;
    addTag("占卜过");
    if (Math.random() < 0.3) {
      effects.mysticism = (effects.mysticism || 0) + 1; // 偶有吉兆
    }
  }
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
  // 生存优先：身体撑不住就休息，没钱就工作，压力爆表就社交
  if (state.stats.health < 45 || state.stats.stamina < 35) {
    return "rest";
  }
  if (state.stats.money < 60) {
    return "work";
  }
  if (state.stats.stress > 70) {
    return "social";
  }
  // 有线索优先调查/推理，推进异常与主线
  if (state.clues.length >= 2 && state.stats.money >= 40 && state.stats.corruption >= 3) {
    if (getInvestigationCooldown() <= 0 && Math.random() < 0.45) {
      return "investigate";
    }
  }
  // V0.23 途径：占卜家偶发占卜（攒神秘知识，耗灵性）；观众社交加成在取效果时处理
  const pathway = state.character?.pathway;
  if (
    pathway === "占卜家" &&
    state.stats.mysticism < 40 &&
    state.stats.money >= 40 &&
    Math.random() < 0.18
  ) {
    return "divination";
  }
  if (state.clues.length >= 2 && state.deductions.length < 4 && Math.random() < 0.25) {
    return "deduce";
  }
  // 有余钱时定期存款
  if (state.stats.money >= 40 && state.finance.savings < 120 && Math.random() < 0.12) {
    return "save";
  }
  // 日常节奏
  const pool = ["study", "work", "rest", "social", "wander"];
  return pool[Math.floor(Math.random() * pool.length)];
}

/** 自动生活：主角自己过一天；若触发待处理事件则停下等待玩家选择。 */
function liveAutomaticDay() {
  if (state.pendingEvent) {
    return false; // 事件待玩家选择
  }
  const actionId = pickAutoAction();
  takeAction(actionId, false); // silent：不逐次渲染
  return !state.pendingEvent; // true = 今天没触发事件，可继续自动
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
    // V0.23：过完一年 → 弹年度人生总结
    showLifeSummary();
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

/** V0.23：一年过完 → 弹年度人生总结（Web 版，规则拼装不 AI）。 */
function buildLifeSummary() {
  const c = state.character;
  // 熟人圈：按友谊排 top3
  const people = Object.entries(state.contacts)
    .map(([id, contact]) => ({
      id,
      name: contact.name,
      job: contact.job,
      friendship: contact.trust ?? 0,
      level: getRelationshipTier(contact.trust) || "生面孔",
    }))
    .filter((p) => p.friendship > 0)
    .sort((a, b) => b.friendship - a.friendship)
    .slice(0, 3);
  const peopleLine =
    people.length > 0
      ? `这一年你认识了：${people
          .map((p) => `${p.name}（${p.job}，${p.level}）`)
          .join("、")}。`
      : "这一年你在廷根多是独来独往。";

  // 经历：从标签粗分
  const tags = state.tags || [];
  const mysticTags = tags.filter(
    (t) => /途径|组织|教会|失控|神秘|失踪/.test(t),
  );
  const expLine = mysticTags.length
    ? `你触碰过异常的世界：${mysticTags.slice(0, 4).join("、")}。`
    : "这一年你过着再普通不过的日子，没有麻烦找上门。";

  // 途径
  const pathway = c.pathway;
  const pathwayLine = pathway
    ? `这一年你踏上了「${pathway}」之路，灵性与疯狂之间，你的选择开始留下痕迹。`
    : "这一年你始终是个普通人。有些门打开过又关上了，但你选择了留下。";

  // 城市回声
  const echoes = (state.world.bulletin || []).map((b) => b.text).filter(Boolean);
  const cityLine = echoes.length
    ? `廷根这一年：${echoes[0]}`
    : "廷根城里，时光照常流淌。";

  // 一句话总结
  let oneLiner = `${c.name}在廷根度过了整整一年`;
  if (pathway) oneLiner += `，以「${pathway}」的身份`;
  if (c.money > 300) oneLiner += "，攒下了一笔积蓄";
  else if (c.money < 20) oneLiner += "，日子过得紧巴巴";
  oneLiner += "。岁月如河，你留下了自己的痕迹。";

  return {
    year: `第五纪 ${state.year}`,
    character: `${c.name} · ${c.age}岁 · ${c.job}`,
    people: peopleLine,
    experiences: expLine,
    pathway: pathwayLine,
    city: cityLine,
    oneliner: oneLiner,
  };
}

function showLifeSummary() {
  const report = buildLifeSummary();
  const panel = document.getElementById("summaryPanel");
  if (!panel) {
    return;
  }
  document.getElementById("summaryYear").textContent = report.year;
  document.getElementById("summaryCharacter").textContent = report.character;
  document.getElementById("summaryPathway").textContent = report.pathway;
  document.getElementById("summaryPeople").textContent = report.people;
  document.getElementById("summaryExperiences").textContent = report.experiences;
  document.getElementById("summaryCity").textContent = report.city;
  document.getElementById("summaryOneliner").textContent = report.oneliner;
  panel.classList.remove("hidden");

  // 存一下报告避免重复弹（记住已展示的年份，避免继续玩时反复弹）
  state.ui.lastSummaryYear = state.year;
  saveState();
  render();
}

function worldTick() {
  state.world.tickCount += 1;
  reduceInvestigationCooldown();
  updateNpcLives(state);
  tickEconomy();
  tickLocations();
  tickMadness();
  tickOrganizations();
  tickExpiredEvents();
  tickCityTidings();
  updateStoryArcs();
}

/** V0.20：城市每日见闻——让玩家感受到城市在运行（与 Python city.news 语义一致）。 */
function tickCityTidings() {
  const month = state.month || 1;
  const candidates = [];
  // 失踪优先（刚发生 3 天内才是新闻）
  const missing = Object.values(state.contacts).filter(
    (c) => c.disappeared && c._disappearedAt !== undefined && state.daysLived - c._disappearedAt <= 3,
  );
  if (missing.length > 0) {
    const names = missing.slice(0, 2).map((c) => c.name).join("、");
    candidates.push(`${names}已经好几天不见人影了，街坊们小声议论着。`);
  }
  const pressure = state.world.economyPressure || 0;
  if (pressure >= 70) candidates.push("煤价与面包价又涨了一截，市场里到处是压低的抱怨声。");
  else if (pressure >= 45) candidates.push("最近物价不太稳，摊贩们说货运越来越不好走。");
  const secret = state.world.organizations?.["暗流组织"]?.activity || 0;
  const church = state.world.organizations?.["黑夜教会"]?.attention || 0;
  if (secret >= 60) candidates.unshift("夜里东区多了些不该有的动静，守夜人一遍遍巡查看不出端倪。");
  else if (church >= 65) candidates.unshift("教堂的信徒今早多了许多，教士们低声说着什么。");
  const eastDanger = state.world.locations?.east?.danger || state.world.locations?.["东区"]?.danger || 0;
  if (eastDanger >= 65) candidates.push("巡警说东区最近不太平，劝人夜里少走深巷。");
  if (candidates.length === 0) {
    if (month === 12 || month === 1 || month === 2) candidates.push("湿冷的冬天，屋檐下晾的衣服三天都不干。");
    else if (month >= 3 && month <= 5) candidates.push("开春了，街道上的雪水化成泥，马车夫都在骂路难走。");
    else candidates.push("廷根今日风平浪静，和昨天没什么两样。");
  }
  state.world.dailyTidings = candidates[0];
}

function getCityTidings() {
  return state.world.dailyTidings || "廷根人的生活，一如既往。";
}

/**
 * 时效与错过痕迹：一次性事件超过 maxDay 后写一条"错过"日志（每事件一次）。
 * 拟真：车站的启事会撤、旧报纸会被收走、符号会被抹去——没赶上就真的错过了。
 */
const EXPIRED_TRACES = {
  station_notice: "你后来想起，车站布告栏上那张失踪启事不知何时被撤下了。你错过了第一次读它的机会。",
  newspaper_overlap: "你翻完旧报纸，发现那条东区失踪的短讯早已过时。线索凉了。",
  strange_symbol: "你再去那条小巷，灰浆已经干透，符号再也看不见了。",
  east_followed: "那段时间过后，你再也没感受到被注视的目光。你错过了确认被跟踪的机会。",
  priest_coin: "你很久没去教堂后室，奥尔森教士把那枚旧硬币收了起来。",
  east_deep_night: "深夜的东区恢复了安静，那扇透出微光的门再也找不到了。",
  symbol_dream: "那阵子之后，你再也没做过那样的梦。",
};

function tickExpiredEvents() {
  if (!state.world.expiredTraced) {
    state.world.expiredTraced = {};
  }
  const traced = state.world.expiredTraced;
  Object.entries(EXPIRED_TRACES).forEach(([eventId, trace]) => {
    if (traced[eventId]) {
      return;
    }
    const event = events.find((e) => e.id === eventId);
    if (!event || event.maxDay === undefined) {
      return;
    }
    // 事件未触发且已过窗口 → 留痕。已触发的判定：
    // 1) onceTag 已获得；2) 任一 choice 产出的标签已获得；3) 关联图节点已完成
    let alreadySeen = false;
    if (event.onceTag && state.tags.includes(event.onceTag)) {
      alreadySeen = true;
    }
    if (!alreadySeen && event.choices) {
      const choiceTags = event.choices.flatMap((c) => c.addTags || []);
      if (choiceTags.some((t) => state.tags.includes(t))) {
        alreadySeen = true;
      }
    }
    if (!alreadySeen) {
      const graphNode = getEventGraphNode(event.id);
      if (graphNode && (state.world.eventGraph.completedNodes || []).includes(graphNode.id)) {
        alreadySeen = true;
      }
    }
    if (alreadySeen) {
      return;
    }
    if (state.daysLived > event.maxDay) {
      traced[eventId] = state.daysLived;
      addEntry(formatDate(), `（错过）${trace}`);
    }
  });
}

function tickMadness() {
  // 非凡代价：隐藏的疯狂值，UI 只显阶段不显数值
  let drift = (state.stats.corruption || 0) / 10 * 0.5;
  if (state.stats.stress > 60) drift += 0.3;
  if (state.stats.spirituality >= 60) drift -= 0.5;
  else if (state.stats.spirituality >= 25) drift -= 0.2;
  state.stats.madness = Math.max(
    0,
    Math.min(100, Math.round((state.stats.madness || 0) + drift)),
  );
}

function getMadnessStage() {
  const m = state.stats.madness || 0;
  if (m >= 70) return "濒危";
  if (m >= 40) return "不安";
  if (m >= 20) return "恍惚";
  return "平稳";
}

function updateContactSchedules(targetState) {
  updateNpcLives(targetState);
}

function updateNpcLives(targetState) {
  Object.values(targetState.contacts).forEach((contact) => {
    if (contact.disappeared) {
      contact.currentActivity = "（失踪）";
      return;
    }
    const dayIndex = targetState.daysLived % 7;
    const isWeekend = dayIndex === 5 || dayIndex === 6;
    const weekendRoutine = contact.weekendRoutine || [];
    if (isWeekend && weekendRoutine.length > 0) {
      const routine = weekendRoutine[dayIndex % weekendRoutine.length];
      contact.currentLocationId = routine.locationId;
      contact.currentActivity = routine.activity;
      return;
    }
    if (contact.routine && contact.routine.length > 0) {
      const routine = contact.routine[dayIndex % contact.routine.length];
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

function tickOrganizations() {
  // 组织行动层：黑夜教会注意度 + 暗流组织活跃度 逐日演化
  if (!state.world.organizations) {
    state.world.organizations = {
      黑夜教会: { attention: 0 },
      暗流组织: { activity: 0 },
    };
  }
  const church = state.world.organizations["黑夜教会"] || { attention: 0 };
  const secret = state.world.organizations["暗流组织"] || { activity: 0 };
  const clues = state.clues || [];
  const tags = state.tags || [];

  // 教会注意度：线索引起注意，沾染异常被察，向教会靠拢显著抬高
  let attention = church.attention - 1;
  attention += Math.min(3, Math.max(0, clues.length - 1));
  if ((state.stats.corruption || 0) >= 5) attention += 1;
  if (tags.some((t) => ["向教会举报", "向教士坦白", "成为教会线人"].includes(t))) {
    attention += 3;
  }
  church.attention = Math.max(0, Math.min(100, attention));

  // 暗流组织：越靠近非凡越活跃，活跃反推城市紧张
  let activity = secret.activity - 1;
  if (tags.some((t) => ["初涉非凡", "完成第二件委托", "加入神秘组织"].includes(t))) {
    activity += 2;
  }
  if ((state.stats.corruption || 0) >= 10) activity += 1;
  secret.activity = Math.max(0, Math.min(100, activity));

  state.world.organizations["黑夜教会"] = church;
  state.world.organizations["暗流组织"] = secret;
  if (secret.activity > 40) {
    state.world.cityTension = Math.max(0, Math.min(100, state.world.cityTension + 1));
  }
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
  const mysticTotal = eventGraphNodes.filter(
    (node) => node.type === "mystic" && node.graphId === "非凡接触",
  ).length;
  const mainlineTotal = eventGraphNodes.filter(
    (node) => node.type === "mystic" && node.graphId === "廷根的暗流",
  ).length;
  const completed = new Set(state.world.eventGraph.completedNodes || []);
  return {
    ordinaryTotal,
    abnormalTotal,
    mysticTotal,
    mainlineTotal,
    ordinaryDone: eventGraphNodes.filter(
      (node) => node.type === "ordinary" && completed.has(node.id),
    ).length,
    abnormalDone: eventGraphNodes.filter(
      (node) => node.type === "abnormal" && completed.has(node.id),
    ).length,
    mysticDone: eventGraphNodes.filter(
      (node) => node.type === "mystic" && node.graphId === "非凡接触" && completed.has(node.id),
    ).length,
    mainlineDone: eventGraphNodes.filter(
      (node) => node.type === "mystic" && node.graphId === "廷根的暗流" && completed.has(node.id),
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

  // 存款利息：月利率 2%，每 50 镑存款每月得 1 镑
  const savings = state.finance.savings || 0;
  const interest = Math.floor(savings / 50);
  if (interest > 0) {
    state.finance.savings += interest;
    summary += ` 存款获得利息 ${interest} 镑（共存 ${state.finance.savings} 镑）。`;
  }

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

  applyEffects({ money: salaryPaid - remainingRent + interest });

  if (state.stats.money <= 0) {
    // 现金见底时，从存款支取救急
    const withdrawn = Math.min(savings, 20);
    if (withdrawn > 0) {
      state.finance.savings -= withdrawn;
      state.stats.money += withdrawn;
      summary += ` 你从存款支取了 ${withdrawn} 镑救急（存款剩 ${state.finance.savings} 镑）。`;
    }
  }

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
  // V0.25 记忆：明显的善意/恶意会被记住
  recordMemory(contact, amount);
}

function changeTrustCapped(contactId, amount, cap) {
  const contact = state.contacts[contactId];
  if (!contact) {
    return 0;
  }
  const before = contact.trust;
  contact.trust = Math.max(0, Math.min(cap, contact.trust + amount));
  const applied = contact.trust - before;
  if (applied !== 0) {
    recordMemory(contact, applied);
  }
  return applied;
}

/** V0.25：记录轻量记忆（contact.memories.helped/harmed 计数）。 */
function recordMemory(contact, applied) {
  if (Math.abs(applied) < 2) {
    return; // 小幅波动不记
  }
  contact.memories = contact.memories || { helped: 0, harmed: 0 };
  if (applied > 0) {
    contact.memories.helped = (contact.memories.helped || 0) + 1;
  } else {
    contact.memories.harmed = (contact.memories.harmed || 0) + 1;
  }
}

/** 泛社交：同地点联系人 +1 信任，但封顶 40（朋友），浅交无法更深。 */
function socializeBroadly(amount = 1) {
  let added = 0;
  Object.entries(state.contacts).forEach(([contactId, contact]) => {
    if (getContactLocation(contact) !== state.locationId) {
      return;
    }
    added += changeTrustCapped(contactId, amount, 40);
  });
  return added;
}

/** 深交：只对选定的深交对象生效，且数额更大、无朋友封顶。 */
function socializeFocused(amount = 3) {
  const contactId = state.ui.focusedContactId;
  if (!contactId || !state.contacts[contactId]) {
    return null;
  }
  const contact = state.contacts[contactId];
  if (getContactLocation(contact) !== state.locationId) {
    return false; // 深交对象不在这里
  }
  changeTrust(contactId, amount);
  return true;
}

function getFocusedContact() {
  const contactId = state.ui.focusedContactId;
  return (contactId && state.contacts[contactId]) || null;
}

function toggleFocusedContact(contactId) {
  if (state.ui.focusedContactId === contactId) {
    state.ui.focusedContactId = null;
    return false;
  }
  if (!state.contacts[contactId]) {
    return false;
  }
  state.ui.focusedContactId = contactId;
  return true;
}

function getRelationshipTier(trust) {
  if (trust >= 80) return "挚友";
  if (trust >= 60) return "密友";
  if (trust >= 40) return "朋友";
  if (trust >= 20) return "熟人";
  return "生面孔";
}

function getRelationshipTierId(trust) {
  if (trust >= 80) return "close";
  if (trust >= 60) return "intimate";
  if (trust >= 40) return "friend";
  if (trust >= 20) return "acquaintance";
  return "stranger";
}

function improveLocalContacts(amount) {
  Object.entries(state.contacts).forEach(([contactId, contact]) => {
    if (getContactLocation(contact) === state.locationId) {
      changeTrustCapped(contactId, amount, 40);
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

  let flavor = "";
  if (actionId === "social") {
    // 先处理深交对象：如果选中了深交对象且同地，专门互动（无封顶、收益大）
    const focusedResult = socializeFocused(3);
    const focused = getFocusedContact();
    const localContacts = Object.values(state.contacts).filter(
      (contact) => getContactLocation(contact) === state.locationId,
    );
    if (focusedResult === true && focused) {
      changeLife({ comfort: 6, stress: -4 });
      const fTier = getRelationshipTier(focused.trust);
      flavor = `你把今天的时间主要留给了${focused.name}（${fTier}）。你们聊了很久，关系明显更近了。`;
    } else if (focusedResult === false && focused) {
      // 深交对象不在此地 → 只能泛社交
      changeLife({ comfort: 2, stress: -1 });
      flavor = `你想找${focused.name}，但他今天不在这里。你只好和附近的人随便聊了几句。`;
    } else if (localContacts.length > 0) {
      const added = socializeBroadly(1);
      const bestTier = Math.max(...localContacts.map((c) => c.trust));
      const tierId = getRelationshipTierId(bestTier);
      if (added === 0) {
        flavor = "你和附近的熟人点头示意，但没有深入交谈。";
      } else if (tierId === "stranger") {
        flavor = "大多是生面孔，你礼貌地问候了几句。";
      } else if (tierId === "acquaintance") {
        flavor = "和几个熟人聊了聊天气和煤价。";
      } else if (tierId === "friend") {
        changeLife({ comfort: 2 });
        flavor = "有朋友在你身边喝酒大笑，这一晚不算难过。";
      } else if (tierId === "intimate") {
        changeLife({ comfort: 4, stress: -2 });
        flavor = "密友看得出你脸色不好，把热茶推到你面前。";
      } else {
        changeLife({ comfort: 5, stress: -3 });
        flavor = "你与挚友并肩坐了很久，不需要说太多话。";
      }
      if (focused && state.ui.focusedContactId) {
        flavor += ` （泛社交封顶于朋友，要继续深交，选中${focused.name}并到TA所在的${getLocation().name}见面。）`;
      }
    } else {
      flavor = "这里没有熟面孔，你独自坐了一会儿。";
    }
  }
  return applyLifePressure() + (flavor ? ` ${flavor}` : "");
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

function renderAutoLifeBadge() {
  const badge = document.getElementById("autoLifeBadge");
  if (!badge) {
    return;
  }
  badge.textContent = "自动生活 · 一天早午晚三程";
  badge.classList.add("on");
  badge.classList.remove("off");
}

function render() {
  renderCharacter();
  ids.forEach((id) => {
    document.getElementById(id).textContent = state.stats[id];
  });
  document.getElementById("date").textContent = formatDate();
  document.getElementById("dayCount").textContent = `第 ${state.daysLived + 1} 天`;
  renderAutoLifeBadge();
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
  renderPathway();
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
  document.getElementById("churchAttention").textContent =
    state.world.organizations?.["黑夜教会"]?.attention ?? 0;
  document.getElementById("secretActivity").textContent =
    state.world.organizations?.["暗流组织"]?.activity ?? 0;
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
  document.getElementById("mainlineGraphCount").textContent =
    `${graphSummary.mainlineDone}/${graphSummary.mainlineTotal}`;
  document.getElementById("madnessStage").textContent = getMadnessStage();
  document.getElementById("npcScheduleCount").textContent =
    `${npcSummary.scheduled}/${npcSummary.total}`;
  const tidingsEl = document.getElementById("cityTidings");
  if (tidingsEl) {
    tidingsEl.textContent = `廷根 · ${getCityTidings()}`;
  }
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
  document.getElementById("bankSavings").textContent = state.finance.savings || 0;

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

function renderPathway() {
  const el = document.getElementById("pathway");
  if (!el) {
    return;
  }
  const c = state.character || {};
  if (!c.pathway) {
    el.textContent = "无";
    return;
  }
  const seqNames = {
    占卜家: { 7: "魔术师", 8: "小丑", 9: "占卜家" },
    观众: { 7: "心理医生", 8: "读心者", 9: "观众" },
    不眠者: { 7: "梦魇", 8: "午夜诗人", 9: "不眠者" },
  };
  const seq = c.sequence ?? 9;
  const name = (seqNames[c.pathway] || {})[seq] || c.pathway;
  if (c.dead) {
    el.textContent = `${name}·已失控`;
  } else if (seq >= 9 && c.sequence === undefined) {
    el.textContent = c.pathway;
  } else {
    el.textContent = `${name}·序列${seq}`;
  }
}

function renderContacts() {
  const contacts = document.getElementById("contacts");
  const entries = Object.entries(state.contacts);
  if (entries.length === 0) {
    contacts.innerHTML = `<span class="empty-tag">暂无</span>`;
    return;
  }

  const focusedId = state.ui.focusedContactId;
  contacts.innerHTML = entries
    .map(([contactId, contact]) => {
      const contactLocationId = getContactLocation(contact);
      const location = locations[contactLocationId] || locations.north;
      const nearby = contactLocationId === state.locationId ? " nearby" : "";
      const focused = contactId === focusedId ? " focused" : "";
      const tier = getRelationshipTier(contact.trust);
      const tierClass = `tier-${getRelationshipTierId(contact.trust)}`;
      const deepHint =
        contact.trust >= 40
          ? `<span class="deep-only">已在朋友之上，需专门深交</span>`
          : "";
      // V0.25：轻量记忆徽记（帮过/坑过，颜色区分）
      const memBadges = [];
      const mem = contact.memories || {};
      if ((mem.helped || 0) > 0) {
        memBadges.push('<em class="mem-badge mem-helped">念着我的好</em>');
      }
      if ((mem.harmed || 0) > 0) {
        memBadges.push('<em class="mem-badge mem-harmed">对我有怨</em>');
      }
      return `
        <article class="contact${nearby}${focused}" data-contact-id="${contactId}">
          <div>
            <strong>${contact.name} <em class="tier-label ${tierClass}">${tier}</em>${focused ? '<em class="focused-tag">深交中</em>' : ""}</strong>
            <span>${contact.role} · ${location.name}</span>
            <span>${contact.currentActivity || "维持日常生活"}</span>
          </div>
          <b class="trust-num">${contact.trust}</b>
          ${memBadges.join("")}
          ${deepHint}
        </article>
      `;
    })
    .join("");

  contacts.querySelectorAll("[data-contact-id]").forEach((card) => {
    card.addEventListener("click", () => {
      toggleFocusedContact(card.dataset.contactId);
      renderContacts();
    });
  });
}

function renderPendingEvent() {
  const panel = document.getElementById("eventPanel");
  const event = state.pendingEvent;

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

/* ---- 多槽位手动存档 ---- */

const SLOT_KEY_PREFIX = "mysteries-slot-";
const SLOT_META_KEY = "mysteries-slot-meta";
let selectedSlot = null;

function slotKey(slotId) {
  return `${SLOT_KEY_PREFIX}${slotId}`;
}

function getSlotMeta() {
  try {
    return JSON.parse(localStorage.getItem(SLOT_META_KEY)) || {};
  } catch {
    return {};
  }
}

function setSlotMeta(meta) {
  localStorage.setItem(SLOT_META_KEY, JSON.stringify(meta));
}

function listSlots() {
  const meta = getSlotMeta();
  const ids = Object.keys(meta)
    .map(Number)
    .sort((a, b) => a - b);
  return ids.map((id) => ({ id, ...meta[id] }));
}

function nextEmptySlot() {
  const meta = getSlotMeta();
  let id = 1;
  while (meta[id]) {
    id += 1;
  }
  return id;
}

function saveToSlot(slotId) {
  const meta = getSlotMeta();
  const entry = {
    savedAt: formatDate(),
    name: state.character.name,
    day: state.daysLived,
    date: `${state.year}年${state.month}月${state.day}日`,
    money: state.stats.money,
    job: getCareer().name,
  };
  meta[slotId] = entry;
  setSlotMeta(meta);
  localStorage.setItem(slotKey(slotId), JSON.stringify(state));
  return entry;
}

function loadSlot(slotId) {
  const raw = localStorage.getItem(slotKey(slotId));
  if (!raw) {
    showSaveToast("该槽位没有存档");
    return null;
  }
  try {
    state = normalizeState(JSON.parse(raw));
    selectedSlot = slotId;
    saveState();
    render();
    renderSavePanel();
    showSaveToast("已读取存档");
    return state;
  } catch {
    showSaveToast("存档损坏，无法读取");
    return null;
  }
}

function deleteSlot(slotId) {
  const meta = getSlotMeta();
  delete meta[slotId];
  setSlotMeta(meta);
  localStorage.removeItem(slotKey(slotId));
  if (selectedSlot === slotId) {
    selectedSlot = null;
  }
  renderSavePanel();
  showSaveToast("已删除存档");
}

function saveToNewSlot() {
  const id = nextEmptySlot();
  saveToSlot(id);
  selectedSlot = id;
  renderSavePanel();
  showSaveToast(`已保存到槽位 ${id}`);
}

function showSaveToast(text) {
  const toast = document.getElementById("saveToast");
  if (!toast) {
    return;
  }
  toast.textContent = text;
  toast.classList.add("show");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove("show"), 1800);
}

function renderSavePanel() {
  const list = document.getElementById("saveSlotList");
  if (!list) {
    return;
  }
  const slots = listSlots();
  const selectedId = selectedSlot;
  if (slots.length === 0) {
    list.innerHTML = `<div class="save-slot-empty">还没有手动存档。<br>先选一个行动推进几天，再回来保存你的分岔人生。</div>`;
    return;
  }
  list.innerHTML = slots
    .map(
      (slot) => `
      <button class="save-slot${slot.id === selectedId ? " selected" : ""}" data-slot-id="${slot.id}" type="button">
        <div>
          <div class="save-slot-title">槽位 ${slot.id} · ${slot.name}</div>
          <div class="save-slot-meta">${slot.date} · 第 ${slot.day + 1} 天 · ${slot.job} · £${slot.money}</div>
        </div>
        <span class="save-slot-time">${slot.savedAt}</span>
      </button>`,
    )
    .join("");
  list.querySelectorAll("[data-slot-id]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedSlot = Number(button.dataset.slotId);
      renderSavePanel();
    });
  });
}

function openSavePanel() {
  renderSavePanel();
  document.getElementById("savePanel").classList.remove("hidden");
}

function closeSavePanel() {
  document.getElementById("savePanel").classList.add("hidden");
}

document.getElementById("openSaves").addEventListener("click", openSavePanel);
document.getElementById("closeSaves").addEventListener("click", closeSavePanel);
document.getElementById("saveToNewSlot").addEventListener("click", saveToNewSlot);
document.getElementById("overwriteSlot").addEventListener("click", () => {
  if (selectedSlot) {
    saveToSlot(selectedSlot);
    renderSavePanel();
    showSaveToast(`已覆盖槽位 ${selectedSlot}`);
  } else {
    showSaveToast("先在列表中选择一个存档槽位");
  }
});
document.getElementById("reloadSlot").addEventListener("click", () => {
  if (selectedSlot) {
    loadSlot(selectedSlot);
  } else {
    showSaveToast("先在列表中选择一个存档槽位");
  }
});
document.getElementById("deleteSlot").addEventListener("click", () => {
  if (selectedSlot) {
    deleteSlot(selectedSlot);
  } else {
    showSaveToast("先在列表中选择一个存档槽位");
  }
});

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
      autoPlay: false, // 自动连播是运行时状态，不随存档恢复
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
    eventLastTriggered: savedWorld.eventLastTriggered || {},
    organizations: {
      黑夜教会: { attention: 0 },
      ...(savedWorld.organizations?.["黑夜教会"] ? { 黑夜教会: savedWorld.organizations["黑夜教会"] } : {}),
      暗流组织: { activity: 0 },
      ...(savedWorld.organizations?.["暗流组织"] ? { 暗流组织: savedWorld.organizations["暗流组织"] } : {}),
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
