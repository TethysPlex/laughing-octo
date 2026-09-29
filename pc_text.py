HELP = (
    "角色管理:\n"
    ".pc new <角色名> // 新建角色并绑卡\n"
    ".pc tag [<角色名> | <角色序号>] // 当前群绑卡/解除绑卡(不填角色名)\n"
    ".pc untagAll [<角色名> | <角色序号>] // 全部群解绑(不填即当前卡)\n"
    ".pc list // 列出当前角色和序号\n"
    ".pc rename <新角色名> // 将当前绑定角色改名\n"
    ".pc rename <角色名|序号> <新角色名> // 将指定角色改名 \n"
    ".pc save [<角色名>] // [不绑卡]保存角色，角色名可省略\n"
    ".pc load (<角色名> | <角色序号>) // [不绑卡]加载角色\n"
    ".pc del/rm (<角色名> | <角色序号>) // 删除角色 角色序号可用pc list查询\n"
    "> 注: 各群数据独立(多张空白卡)，单群游戏不需要存角色。"
)
NEW = "新建角色且自动绑定: {name}"
EXISTS = "已存在同名角色"
TAG = '切换角色"{name}"，绑定成功'
TAG_MISSING = '角色"{name}"绑定失败，角色不存在'
UNTAG = '角色"{name}"绑定已解除，切换至群内角色卡'
NOT_BOUND = "当前群内并未绑定角色"
LOADED = "角色<{name}>加载成功，欢迎回来"
MISSING = "无法加载/删除角色：你所指定的角色不存在"
INVALID_DATA = "无法加载/保存角色：序列化失败"
SAVED = '角色"{name}"储存成功\n注: 非秘密团不用开团前存卡，跑团后save即可'
SAVE_BOUND = '角色卡"{name}"是绑定状态，无法进行save操作'
DELETED = '角色"{name}"删除成功'
DELETE_BOUND = '角色卡"{name}"是绑定状态，".pc untagAll {name}"解除绑卡后再操作吧'
DELETE_FAILED = "角色删除失败"
RENAMED = "操作完成"
RENAME_EXISTS = "此角色名已存在"
RENAME_MISSING = "未找到此角色"
UNBOUND_ALL = "绑定已全部解除:\n{groups}"
NO_BINDINGS = "这张卡片并未绑定到任何群"
EMPTY_LIST = "<{player}>当前还没有角色列表"
LIST = "<{player}>的角色列表为:\n{rows}\n[√]已绑 [×]未绑 [★]其他群绑定"
