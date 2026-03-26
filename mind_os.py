import json
import os
from datetime import datetime

class Storage:
    """Handles storing and retrieving MindOS data (thoughts, decisions, actions)."""
    def __init__(self, filename="mindos_data.json"):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(self.filename):
            return {"logs": [], "streak": 0, "difficulty_modifier": 1.0}
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"logs": [], "streak": 0, "difficulty_modifier": 1.0}

    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_log(self, log_entry):
        if "timestamp" not in log_entry:
            log_entry["timestamp"] = datetime.now().isoformat()
        self.data["logs"].append(log_entry)
        self.save_data()


class ThoughtAnalyzer:
    """Analyzes user thoughts for negative patterns."""
    def __init__(self):
        # Phrases that indicate positive intent despite containing negative words
        self.positive_overrides = [
            "don't quit", "won't quit", "not quitting", "never quit",
            "don't give up", "won't give up", "never give up", "not giving up",
            "not afraid", "not skipping", "won't skip", "not lazy",
            "not tired", "don't avoid", "not avoiding", "won't stop",
            "don't stop", "not stopping"
        ]
        
        # Words indicating avoidance/delay
        self.avoidance_keywords = [
            "skip", "skipping", "delay", "postpone", "procrastinate", 
            "tomorrow", "later", "avoid", "avoiding", "not feeling like"
        ]
        
        # Words indicating fear/stress/weakness/negativity
        self.fear_stress_keywords = [
            "fear", "scared", "stress", "anxious", "overwhelmed", "hard", 
            "difficult", "too much", "lazy", "tired", "exhausted", "give up", 
            "quit", "can't", "cannot", "won't", "don't want to", "do not want to"
        ]

    def analyze(self, thought):
        thought_lower = thought.lower()
        
        # Mask positive overrides so they don't trigger negative keywords
        masked_thought = thought_lower
        for phrase in self.positive_overrides:
            masked_thought = masked_thought.replace(phrase, " [positive_override] ")
            
        found_avoidance = [kw for kw in self.avoidance_keywords if kw in masked_thought]
        found_fear = [kw for kw in self.fear_stress_keywords if kw in masked_thought]
        
        all_found = found_avoidance + found_fear
        
        analysis = {
            "thought": thought,
            "keywords_detected": list(set(all_found)),
            "is_negative": len(all_found) > 0,
            "questions": []
        }
        
        if analysis["is_negative"]:
            if found_avoidance:
                analysis["questions"].extend([
                    "Are you delaying this out of genuine necessity, or are you just avoiding the effort?",
                    "What happens if you keep pushing this to another time?"
                ])
            elif any(k in found_fear for k in ["fear", "scared", "stress", "anxious", "overwhelmed"]):
                analysis["questions"].extend([
                    "What is the worst that could happen?",
                    "Is the stress coming from lack of preparation?"
                ])
            elif any(k in found_fear for k in ["lazy", "tired", "exhausted", "hard", "difficult"]):
                analysis["questions"].append("Are you actually physically exhausted, or just resisting the mental effort?")
            elif any(k in found_fear for k in ["can't", "cannot", "won't", "don't want to", "do not want to", "give up", "quit"]):
                analysis["questions"].append("Are you resisting because it's difficult, or because you lack discipline?")
            else:
                analysis["questions"].append("Is this thought helping you grow, or holding you back?")
        return analysis


class DecisionSimulator:
    """Simulates the short-term and long-term consequences of a decision."""
    def simulate(self, is_avoiding):
        if is_avoiding:
            short_term = "Temporary relief from anxiety or effort."
            long_term = "Increased future stress, lowered self-esteem, compounding difficulty of the task."
            impact = "NEGATIVE - You are borrowing peace from tomorrow."
        else:
            short_term = "Immediate discomfort and expenditure of energy."
            long_term = "Task completion, skill growth, improved self-respect."
            impact = "POSITIVE - You are investing in your future self."
            
        return {
            "short_term": short_term,
            "long_term": long_term,
            "impact": impact
        }


class DisciplineEnforcer:
    """Forces the user to make a choice between action and penalty."""
    def __init__(self, storage):
        self.storage = storage

    def enforce(self):
        print("\n=== Discipline Enforcer ===")
        print("You have a choice right now. The pain of discipline or the pain of regret.")
        print("1. Take action now")
        print("2. Accept penalty (Avoid/Delay)")
        
        while True:
            choice = input("Enter your choice (1 or 2): ").strip()
            if choice == '1':
                print("\n[+] Excellent. Action overrules doubt. Your streak continues.")
                self.storage.data["streak"] += 1
                self.storage.data["difficulty_modifier"] = 1.0
                action = "Took Action"
                break
            elif choice == '2':
                print("\n[-] Penalty accepted.")
                print("[-] Your current streak has been broken.")
                print("[-] Your next tasks will be artificially assigned a higher difficulty modifier.")
                self.storage.data["streak"] = 0
                self.storage.data["difficulty_modifier"] += 0.5
                action = "Took Penalty"
                break
            else:
                print("Invalid choice. Do not avoid the question.")
        
        self.storage.save_data()
        return action


class TrackingSystem:
    """Tracks patterns, streaks, and provides summaries."""
    def __init__(self, storage):
        self.storage = storage

    def check_patterns(self):
        logs = self.storage.data.get("logs", [])
        avoid_count = sum(1 for log in logs if log.get("action") == "Took Penalty")
        print(f"\n[Pattern Detection]: You have avoided tasks or taken the penalty {avoid_count} times in your recorded history.")
        
        # Reality check mode
        if avoid_count >= 4:
            print("\n!!! REALITY CHECK !!!")
            print("You have developed a chronic habit of avoidance. Stop negotiating with weakness.")
            print("Nobody is going to save you. Do the work.")
            
        print(f"\n[Current Streak]: {self.storage.data.get('streak', 0)} consecutive actions.")
        print(f"[Difficulty Modifier]: {self.storage.data.get('difficulty_modifier', 1.0)}x")

    def daily_summary(self):
        logs = self.storage.data.get("logs", [])
        today_date = datetime.now().date().isoformat()
        today_logs = [log for log in logs if log.get("timestamp", "").startswith(today_date)]
        
        print(f"\n=== Daily Summary ({today_date}) ===")
        print(f"Thoughts logged today : {len(today_logs)}")
        
        actions_taken = sum(1 for log in today_logs if log.get("action") == "Took Action")
        penalties_taken = sum(1 for log in today_logs if log.get("action") == "Took Penalty")
        
        print(f"Tasks Conquered       : {actions_taken}")
        print(f"Penalties Accepted    : {penalties_taken}")
        
        if len(today_logs) > 0:
            success_rate = (actions_taken / len(today_logs)) * 100
            print(f"Daily Success Rate    : {success_rate:.1f}%")


class MindOS:
    """Main application controller for MindOS."""
    def __init__(self):
        # We ensure the persistence points to the project directory
        # so it saves mindos_data.json correctly 
        storage_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mindos_data.json")
        self.storage = Storage(storage_file)
        self.analyzer = ThoughtAnalyzer()
        self.simulator = DecisionSimulator()
        self.enforcer = DisciplineEnforcer(self.storage)
        self.tracker = TrackingSystem(self.storage)

    def run(self):
        print("=" * 50)
        print("    MindOS - Personal Decision & Discipline    ")
        print("=" * 50)
        
        while True:
            print("\n" + "-"*20)
            print("Main Menu:")
            print("1. Log a Thought / Face a Decision")
            print("2. View Patterns & Stats")
            print("3. Daily Summary")
            print("4. Exit MindOS")
            
            choice = input("\nSelect an option: ").strip()
            
            if choice == '1':
                self.process_thought()
            elif choice == '2':
                self.tracker.check_patterns()
            elif choice == '3':
                self.tracker.daily_summary()
            elif choice == '4':
                print("\nShutting down MindOS. Stay disciplined.")
                break
            else:
                print("Invalid option. Please input 1, 2, 3, or 4.")

    def process_thought(self):
        thought = input("\nEnter your current thought/dilemma: ").strip()
        if not thought:
            print("Thought cannot be empty.")
            return

        # 1. Thought Analyzer
        analysis = self.analyzer.analyze(thought)
        
        is_avoiding = False
        if analysis["is_negative"]:
            print("\n[!] Negative/Avoidance Pattern Detected [!]")
            print(f"Trigger words: {', '.join(analysis['keywords_detected'])}")
            print("\nAnswer the following:")
            for q in analysis["questions"]:
                _ = input(f" - {q}\n   > ")
            is_avoiding = True
        else:
            print("\n[+] No obvious negative patterns detected. Good frame of mind.")
            
        # 2. Decision Simulator
        print("\n=== Decision Simulator ===")
        sim_result = self.simulator.simulate(is_avoiding)
        print(f"Short-Term Outcome  : {sim_result['short_term']}")
        print(f"Long-Term Consequence: {sim_result['long_term']}")
        print(f"Reality Impact      : {sim_result['impact']}")
        
        # 3. Discipline Enforcer
        action = self.enforcer.enforce()
        
        # 4. Save to Tracker
        log_entry = {
            "thought": thought,
            "analysis": analysis,
            "simulation": sim_result,
            "action": action
        }
        self.storage.add_log(log_entry)
        print("\n[System] Log saved successfully.")

if __name__ == "__main__":
    app = MindOS()
    app.run()
