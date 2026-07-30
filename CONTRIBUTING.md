# 贡献指南

感谢你对 VAN-PROJECT 的关注！这是一个个人自改房车的开源项目，欢迎任何形式的贡献。

## 项目结构

```
van-project/
├── modules/        # 功能模块：设计决策、施工指导、材料清单
├── docs/           # 部署指南、设计参考、依赖关系图
├── software/       # 代码：仪表盘、HA 配置、开发环境
├── archive/        # 归档：历史草稿
└── TODO.md         # 进度追踪
```

- 设计决策写在 `modules/XX-模块名/design.md`
- 施工指导写在 `modules/XX-模块名/build-guide.md`
- 材料清单写在 `modules/XX-模块名/bom.md`
- 过程照片/图纸放在对应模块的 `assets/` 下

## 如何贡献

### 报告问题 (Issues)

发现 bug、文档错误或有改进建议？请提交 Issue，尽量包含：
- 清晰的问题描述
- 复现步骤（如适用）
- 期望行为与实际行为的对比

### 提交代码 (Pull Requests)

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交你的修改，保持 commit message 清晰
4. 如果是软件改动，确保 `pnpm lint` 和 `pnpm build` 通过
5. 提交 PR，描述清楚改了什么、为什么这样改

### 文档贡献

文档同样重要！如果你有：
- 自改房车的经验想要补充
- 更优的施工工艺
- 替代方案推荐

欢迎直接提 PR 或开 Issue 讨论。

## 文档规范

- 主文档使用中文撰写
- 代码注释和变量名使用英文
- 设计决策放在 `modules/XX-模块名/design.md`
- 施工笔记放在对应 `modules/XX-模块名/build-guide.md`
- 材料清单放在对应 `modules/XX-模块名/bom.md`

## 行为准则

- 尊重他人的改装方案和经验
- 建设性讨论，避免无谓争论
- 房车安全无小事，涉及电路、结构的改动请附上依据

## 联系

如有问题，欢迎提 Issue 讨论。
