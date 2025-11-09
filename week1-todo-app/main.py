import json
from datetime import datetime
from pathlib import Path

# ============================================
# 資料結構設計說明
# ============================================
# 1. tasks_list: List[Dict] - 維持任務插入順序 - O(n)遍歷
# 2. tasks_dict: Dict[int, Dict] - 快速查找任務 - O(1)查找
# 這是一個經典的「用空間換時間」的優化策略
# ============================================

class TodoApp:
    """
    CLI待辦清單應用程序
    
    資料結構設計：
    - tasks_list: 保持順序的列表 (用於遍歷)
    - tasks_dict: ID到任務的映射 (用於快速查找)
    - next_id: 下一個待分配的ID
    """
    
    def __init__(self, filename="tasks.json"):
        """
        初始化應用程序
        
        參數:
            filename (str): 用於持久化存儲的JSON文件名
        
        時間複雜度: O(n) - 需要讀取所有n個任務
        空間複雜度: O(n) - 存儲所有n個任務
        """
        # 讓檔案永遠放在程式所在的資料夾
        self.filename = Path(__file__).parent / filename
        self.tasks_list = []    # List[Dict] - O(n)遍歷
        self.tasks_dict = {}    # Dict[int, Dict] - O(1)查找
        self.next_id = 1        # int - 生成唯一ID的計數器
        self.load_tasks()
    
    def load_tasks(self):
        """
        從JSON文件加載任務到內存
        
        時間複雜度: O(n)
        - JSON反序列化: O(n)
        - 重建字典: O(n)
        - 總計: O(n)
        
        空間複雜度: O(n) - 存儲n個任務
        """
        try:
            if Path(self.filename).exists():
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.tasks_list = json.load(f)
                
                # 重建字典以支持O(1)查找
                # 這就是「用空間換時間」的體現
                for task in self.tasks_list:
                    self.tasks_dict[task["id"]] = task
                
                # 計算下一個可用的ID
                if self.tasks_list:
                    self.next_id = max(task["id"] for task in self.tasks_list) + 1
                
                print(f"✅ 已加載 {len(self.tasks_list)} 個任務")
        except (json.JSONDecodeError, IOError) as e:
            print(f"❌ 加載任務失敗：{e}")
            self.tasks_list = []
            self.tasks_dict = {}
    
    def save_tasks(self):
        """
        將任務保存到JSON文件
        
        時間複雜度: O(n)
        - JSON序列化: O(n)
        - 文件寫入: O(n)
        
        空間複雜度: O(n) - 臨時JSON字符串
        """
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.tasks_list, f, ensure_ascii=False, indent=2)
            print("✅ 任務已保存")
        except IOError as e:
            print(f"❌ 保存任務失敗：{e}")
    
    def add_task(self, title, priority="中"):
        """
        添加新任務
        
        參數:
            title (str): 任務標題
            priority (str): 優先級 ("高"/"中"/"低")
        
        時間複雜度: O(1)
        - 創建字典: O(1)
        - append到列表: O(1)
        - 插入到字典: O(1)
        - 總計: O(1) ✅ 超高效
        
        空間複雜度: O(1) - 只添加一個任務
        """
        task = {
            "id": self.next_id,
            "title": title,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 同時更新兩個數據結構
        self.tasks_list.append(task)              # O(1)
        self.tasks_dict[self.next_id] = task      # O(1)
        self.next_id += 1
        
        self.save_tasks()
        print(f"✅ 任務已添加：{title}")
        return task
    
    def find_task_by_id(self, task_id):
        """
        按ID查找任務
        
        參數:
            task_id (int): 任務ID
        
        返回:
            Dict 或 None
        
        時間複雜度: O(1) ✅ - 直接字典查找
        這比遍歷列表的O(n)快得多！
        
        對比：
        - 字典查找: O(1) ✅
        - 列表遍歷: O(n) ❌
        """
        return self.tasks_dict.get(task_id)
    
    def list_tasks(self, filter_by=None):
        """
        列出所有任務，可選按優先級篩選
        
        參數:
            filter_by (str): 篩選優先級 (None表示全部)
        
        時間複雜度: O(n)
        - 遍歷所有任務: O(n)
        - 無法優化，因為需要顯示所有數據
        
        空間複雜度: O(k) - k是篩選後的任務數
        """
        if not self.tasks_list:
            print("📝 暫無任務")
            return
        
        print("\n" + "="*60)
        print("📋 我的任務")
        print("="*60)
        
        # 構建優先級順序（用於排序）
        priority_order = {"高": 1, "中": 2, "低": 3}
        
        # 篩選任務
        tasks_to_show = self.tasks_list
        if filter_by:
            tasks_to_show = [t for t in self.tasks_list if t["priority"] == filter_by]
        
        # 按優先級排序
        # 時間複雜度: O(n log n) - Python的Timsort
        sorted_tasks = sorted(
            tasks_to_show,
            key=lambda task: priority_order[task["priority"]]
        )
        
        # 顯示任務
        for task in sorted_tasks:
            status = "✓" if task["completed"] else " "
            priority_emoji = {"高": "🔴", "中": "🟡", "低": "🟢"}
            
            print(f"[{status}] ID:{task['id']:2d} | {task['title']:20s} | "
                  f"優先級:{priority_emoji[task['priority']]} | "
                  f"建立:{task['created_at']}")
        
        print("="*60 + "\n")
    
    def complete_task(self, task_id):
        """
        標記任務為完成
        
        參數:
            task_id (int): 任務ID
        
        時間複雜度: O(1)
        - 字典查找: O(1) ✅
        - 更新狀態: O(1)
        - 字典引用更新: O(1)
        - 總計: O(1)
        
        為什麼不遍歷列表找任務？
        因為我們直接從字典中獲取引用，
        而字典中存儲的是指向列表中同一個對象的引用，
        所以修改字典中的對象會自動反映在列表中。
        """
        task = self.find_task_by_id(task_id)
        if task:
            task["completed"] = True
            self.save_tasks()
            print(f"✅ 任務已完成：{task['title']}")
        else:
            print(f"❌ 任務不存在 (ID: {task_id})")
    
    def delete_task(self, task_id):
        """
        刪除任務
        
        參數:
            task_id (int): 任務ID
        
        時間複雜度: O(n)
        分析:
        - 字典查找: O(1)
        - 列表推導: O(n) ← 瓶頸！
        - 字典刪除: O(1)
        - 總計: O(n)
        
        為什麼列表推導是O(n)？
        因為需要遍歷整個列表來構建新列表
        
        改進方案（如果任務超級多）：
        可以在列表中使用索引標記刪除，
        然後定期清理，實現O(1)刪除
        """
        if task_id in self.tasks_dict:
            task = self.tasks_dict[task_id]
            print(f"✅ 已刪除任務：{task['title']}")
            
            # 從字典刪除
            del self.tasks_dict[task_id]  # O(1)
            
            # 從列表刪除（使用列表推導重建列表）
            self.tasks_list = [t for t in self.tasks_list if t["id"] != task_id]  # O(n)
            
            self.save_tasks()
        else:
            print(f"❌ 任務不存在 (ID: {task_id})")
    
    def sort_by_priority(self):
        """
        按優先級排序任務（演示排序算法）
        
        時間複雜度: O(n log n)
        - Python內置sorted()使用Timsort算法
        - Timsort在已排序數據上表現優異
        
        空間複雜度: O(n) - 創建新排序列表
        """
        priority_order = {"高": 1, "中": 2, "低": 3}
        sorted_tasks = sorted(
            self.tasks_list,
            key=lambda task: priority_order[task["priority"]]
        )
        return sorted_tasks
    
    def get_statistics(self):
        """
        獲取任務統計信息
        
        時間複雜度: O(n)
        - 需要遍歷所有任務計數
        """
        total = len(self.tasks_list)
        completed = sum(1 for task in self.tasks_list if task["completed"])
        pending = total - completed
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }
    
    def run(self):
        """
        運行主程序交互循環
        """
        print("\n" + "="*60)
        print("🎯 歡迎使用 CLI 待辦清單應用")
        print("="*60)
        
        while True:
            print("\n【主菜單】")
            print("1. 添加任務")
            print("2. 查看任務")
            print("3. 完成任務")
            print("4. 刪除任務")
            print("5. 查看統計")
            print("6. 按優先級排序")
            print("7. 退出")
            
            choice = input("\n請選擇操作（1-7）：").strip()
            
            if choice == "1":
                title = input("任務標題：").strip()
                if not title:
                    print("❌ 標題不能為空")
                    continue
                priority = input("優先級（高/中/低）[預設：中]：").strip() or "中"
                if priority not in ["高", "中", "低"]:
                    print("❌ 優先級必須是高/中/低")
                    continue
                self.add_task(title, priority)
            
            elif choice == "2":
                self.list_tasks()
            
            elif choice == "3":
                self.list_tasks()
                try:
                    task_id = int(input("要完成的任務ID：").strip())
                    self.complete_task(task_id)
                except ValueError:
                    print("❌ 請輸入有效的ID")
            
            elif choice == "4":
                self.list_tasks()
                try:
                    task_id = int(input("要刪除的任務ID：").strip())
                    self.delete_task(task_id)
                except ValueError:
                    print("❌ 請輸入有效的ID")
            
            elif choice == "5":
                stats = self.get_statistics()
                print("\n📊 任務統計")
                print(f"  總任務數: {stats['total']}")
                print(f"  已完成: {stats['completed']}")
                print(f"  待完成: {stats['pending']}")
                print(f"  完成率: {stats['completion_rate']:.1f}%")
            
            elif choice == "6":
                sorted_tasks = self.sort_by_priority()
                print("\n📌 按優先級排序")
                priority_order = {"高": 1, "中": 2, "低": 3}
                priority_emoji = {"高": "🔴", "中": "🟡", "低": "🟢"}
                for task in sorted_tasks:
                    status = "✓" if task["completed"] else " "
                    print(f"[{status}] {task['title']:20s} | "
                          f"優先級:{priority_emoji[task['priority']]}")
            
            elif choice == "7":
                print("\n👋 再見！")
                break
            
            else:
                print("❌ 無效選擇，請重試")


if __name__ == "__main__":
    app = TodoApp("tasks.json")
    app.run()
