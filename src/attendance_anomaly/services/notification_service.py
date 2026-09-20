"""异常通知服务。

为识别出的考勤异常生成面向不同角色（员工/主管）的通知文案，
便于通过消息、邮件等渠道推送。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from attendance_anomaly.models.attendance import Anomaly

_TYPE_LABEL = {
    "late": "迟到",
    "early_leave": "早退",
    "missing_punch": "缺卡",
    "overtime": "加班",
    "absent": "旷工",
    "weekend_overtime": "休息日加班",
    "consecutive_work": "连续上班",
}


@dataclass
class Notification:
    """一条通知。"""

    recipient_id: str
    role: str
    title: str
    body: str

    def to_dict(self) -> dict:
        return {
            "recipient_id": self.recipient_id,
            "role": self.role,
            "title": self.title,
            "body": self.body,
        }


class NotificationService:
    """考勤异常通知生成器。"""

    def build_notifications(self, anomalies: List[Anomaly]) -> List[Notification]:
        """为每条异常生成员工通知。"""
        notifications: List[Notification] = []
        for anomaly in anomalies:
            label = _TYPE_LABEL.get(anomaly.anomaly_type, anomaly.anomaly_type)
            notifications.append(
                Notification(
                    recipient_id=anomaly.employee_id,
                    role="employee",
                    title=f"考勤异常提醒：{label}",
                    body=f"{anomaly.date} 您存在「{label}」异常：{anomaly.detail}，请及时核对。",
                )
            )
        return notifications

    def build_manager_digest(self, anomalies: List[Anomaly]) -> List[Notification]:
        """为每位主管生成异常汇总通知。"""
        grouped: Dict[str, List[Anomaly]] = {}
        for anomaly in anomalies:
            grouped.setdefault(anomaly.employee_id, []).append(anomaly)

        notifications: List[Notification] = []
        for employee_id, items in sorted(grouped.items()):
            labels = {_TYPE_LABEL.get(a.anomaly_type, a.anomaly_type) for a in items}
            body = f"员工 {employee_id} 本月存在 {len(items)} 条异常，涉及：{'、'.join(sorted(labels))}。"
            notifications.append(
                Notification(
                    recipient_id="manager",
                    role="manager",
                    title="团队考勤异常汇总",
                    body=body,
                )
            )
        return notifications
