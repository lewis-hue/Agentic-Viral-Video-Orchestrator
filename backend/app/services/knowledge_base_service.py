import json
from typing import List
from models.knowledge_base import ViralTip, KnowledgeBase

class KnowledgeBaseService:
    def __init__(self, data_file: str = "data/viral_tips.json"):
        self.data_file = data_file
        self.tips: List[ViralTip] = []
        self.load_tips()

    def load_tips(self):
        with open(self.data_file, 'r') as f:
            data = json.load(f)
            kb = KnowledgeBase(**data)
            self.tips = kb.tips

    def get_tips_by_category(self, category: str) -> List[ViralTip]:
        return [tip for tip in self.tips if tip.category.lower() == category.lower()]

    def get_all_tips(self) -> List[ViralTip]:
        return self.tips

    def get_tip_by_id(self, tip_id: int) -> ViralTip:
        return next((tip for tip in self.tips if tip.id == tip_id), None)