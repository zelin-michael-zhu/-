LOW_RISK = [
    "fill first name",
    "fill last name",
    "fill email",
    "fill nationality",
    "fill university",
    "fill major",
    "fill gpa",
    "upload cv",
    "upload transcript",
    "upload personal statement",
    "click save draft",
    "save draft",
    "click next page",
    "navigate next page",
    "read public program page",
    "generate recommendation",
    "create checklist",
    "填写姓名",
    "填写邮箱",
    "填写学校",
    "填写专业",
    "填写 gpa",
    "上传 cv",
    "上传成绩单",
    "上传个人陈述",
    "保存草稿",
    "下一页",
]

MEDIUM_RISK = [
    "send recommender invitation",
    "send recommendation",
    "invite recommender",
    "edit recommender email",
    "mark section complete",
    "upload official transcript",
    "submit section but not final application",
    "change application answer",
    "发送推荐信",
    "邀请推荐人",
    "修改推荐人邮箱",
    "标记章节完成",
    "上传官方成绩单",
    "提交章节",
]

HIGH_RISK_BLOCKED = [
    "final submit",
    "submit application",
    "payment",
    "application fee",
    "checkout",
    "agree declaration",
    "legal declaration",
    "confirm declaration",
    "certify information",
    "withdraw application",
    "delete application",
    "delete",
    "cancel application",
    "bypass captcha",
    "solve captcha",
    "login using saved password",
    "stored password",
    "最终提交",
    "提交申请",
    "付款",
    "支付",
    "申请费",
    "同意声明",
    "法律声明",
    "确认声明",
    "认证信息",
    "撤回申请",
    "删除申请",
    "删除",
    "取消申请",
    "绕过验证码",
    "破解验证码",
    "自动登录",
]


class RiskGuard:
    def classify(self, action_text: str) -> dict:
        lowered = (action_text or "").lower()
        if any(keyword in lowered for keyword in HIGH_RISK_BLOCKED):
            return {
                "risk_level": "high",
                "requires_approval": True,
                "blocked": True,
                "reason": "High-risk action is blocked. The user must complete this manually on the official portal.",
            }
        if any(keyword in lowered for keyword in MEDIUM_RISK):
            return {
                "risk_level": "medium",
                "requires_approval": True,
                "blocked": False,
                "reason": "This action may notify others, change important information, or complete a section. Human approval is required.",
            }
        if any(keyword in lowered for keyword in LOW_RISK):
            return {
                "risk_level": "low",
                "requires_approval": False,
                "blocked": False,
                "reason": "Low-risk operation can be automated and will be recorded in the audit log.",
            }
        return {
            "risk_level": "low",
            "requires_approval": False,
            "blocked": False,
            "reason": "Low-risk browser action.",
        }
