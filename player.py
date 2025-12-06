"""
Player classes for DICE_ANALYZER.
"""

from abc import ABC, abstractmethod


class Player(ABC):
    """Base player class."""
    
    def __init__(self, name: str, bankroll: int):
        self.name = name
        self.bankroll = bankroll
    
    @abstractmethod
    def get_bet_input(self) -> int:
        """Get bet amount from player. Returns 0 to quit."""
        pass


class HumanPlayer(Player):
    """Human player - gets input from stdin."""
    
    def get_bet_input(self) -> int:
        raw = input()
        if raw.strip().lower() in ('q', 'quit', 'exit'):
            return 0
        return int(raw.replace(',', ''))


class CPUPlayer(Player):
    """CPU player - for future implementation."""
    
    def __init__(self, name: str, bankroll: int, aggression: float = 0.5):
        super().__init__(name, bankroll)
        self.aggression = aggression  # 0.0 = conservative, 1.0 = aggressive
    
    def get_bet_input(self) -> int:
        """Simple betting strategy based on aggression."""
        import random
        
        # Base bet: 1-10% of bankroll depending on aggression
        base_pct = 0.01 + (self.aggression * 0.09)
        variance = random.uniform(0.5, 1.5)
        bet = int(self.bankroll * base_pct * variance)
        
        # Round to nice numbers
        if bet >= 10000:
            bet = (bet // 1000) * 1000
        elif bet >= 1000:
            bet = (bet // 100) * 100
        else:
            bet = max(100, (bet // 10) * 10)
        
        return min(bet, self.bankroll)
