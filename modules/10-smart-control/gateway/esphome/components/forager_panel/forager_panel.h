#pragma once

#include "esphome/core/component.h"
#include "esphome/core/defines.h"
#include "esphome/components/web_server_base/web_server_base.h"
#include "esphome/components/web_server_idf/web_server_idf.h"

namespace esphome {
namespace forager_panel {

/// 自定义 HTTP handler：serve 自包含的 index.html（gzip PROGMEM）到指定路由。
/// 与原生 web_server 共存：原生 REST（/switch、/sensor 等）继续可用，
/// 本组件只接管"页面外壳"这一条 URL。
class ForagerPanel : public Component, public web_server_idf::AsyncWebHandler {
 public:
  ForagerPanel(web_server_base::WebServerBase *base, const std::string &route,
               const uint8_t *data, size_t size)
      : base_(base), route_(route), data_(data), size_(size) {}

  void register_handler() { this->base_->add_handler(this); }

  float get_setup_priority() const override { return setup_priority::AFTER_WIFI; }

  bool canHandle(AsyncWebServerRequest *request) const override {
    if (request->method() != HTTP_GET)
      return false;
    char buf[AsyncWebServerRequest::URL_BUF_SIZE];
    esphome::StringRef url = request->url_to(buf);
    return url == this->route_;
  }

  void handleRequest(AsyncWebServerRequest *request) override {
    AsyncWebServerResponse *response =
        request->beginResponse(200, "text/html", this->data_, this->size_);
    response->addHeader("Content-Encoding", "gzip");
    response->addHeader("Cache-Control", "public, max-age=300");
    request->send(response);
  }

 protected:
  web_server_base::WebServerBase *base_;
  std::string route_;
  const uint8_t *data_;
  size_t size_;
};

}  // namespace forager_panel
}  // namespace esphome
