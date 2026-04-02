# storyboard-schema.md（统一修订版）

## JSON 结构
每个 shot 必须包含：
- scene_description
- image_prompt
- video_prompt
- voice_over_script

## image_prompt 校验
1. 必须包含比例声明。
2. 默认比例为 16:9；用户另有指定时按用户指定。
3. 比例声明写在正向提示词最后。

## scene_description 校验
- 只描述该镜头的任务、场景、动作、光线与构图重点。
- 不重复写全局规则与系统规则。
