import gzip

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import web_server_base
from esphome.components.web_server_base import CONF_WEB_SERVER_BASE_ID
from esphome.const import CONF_ID, CONF_PATH
from esphome.core import CORE, coroutine_with_priority
from esphome.coroutine import CoroPriority

DEPENDENCIES = ["web_server_base", "web_server"]
AUTO_LOAD = ["web_server_base", "web_server"]

forager_panel_ns = cg.esphome_ns.namespace("forager_panel")
ForagerPanel = forager_panel_ns.class_("ForagerPanel", cg.Component)

CONF_HTML_FILE = "html_file"
CONF_ROUTE = "route"

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(ForagerPanel),
        cv.GenerateID(CONF_WEB_SERVER_BASE_ID): cv.use_id(web_server_base.WebServerBase),
        cv.Required(CONF_HTML_FILE): cv.file_,
        cv.Optional(CONF_ROUTE, default="/dashboard"): cv.string,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    paren = await cg.get_variable(config[CONF_WEB_SERVER_BASE_ID])

    # 读 HTML 并 gzip 进 PROGMEM（生成 C++ 全局数组）
    path = CORE.relative_config_path(config[CONF_HTML_FILE])
    with path.open(encoding="utf-8") as f:
        html = f.read().encode("utf-8")
    gz = gzip.compress(html, 9)
    arr_name = "FORAGER_PANEL_INDEX_GZ"
    cg.add_global(
        cg.RawExpression(
            f"const uint8_t {arr_name}[] PROGMEM = {{{', '.join(str(x) for x in gz)}}};"
        )
    )
    cg.add_global(
        cg.RawExpression(f"const size_t {arr_name}_SIZE = {len(gz)};")
    )

    # 实例化组件：base, route, data 指针, size
    var = cg.new_Pvariable(
        config[CONF_ID],
        paren,
        config[CONF_ROUTE],
        cg.RawExpression(arr_name),
        cg.RawExpression(f"{arr_name}_SIZE"),
    )
    await cg.register_component(var, config)
    cg.add(var.register_handler())
