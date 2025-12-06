#!/usr/bin/env python3
"""
DICE_ANALYZER v2.1.3
A totally legitimate business analytics tool.
"""

import random
import time
import shutil
import sys
from datetime import datetime
from player import Player, HumanPlayer, CPUPlayer

# =============================================================================
# CONFIGURATION
# =============================================================================

INITIAL_BANKROLL = 1_000_000
SESSION_ID = f"0x{random.randint(0x1000, 0xFFFF):04X}"
VERSION = "2.1.3"

# Delay settings (seconds)
DELAY_BASE = 0.08
DELAY_JITTER = (-0.03, 0.05)
DELAY_HEAVY = (0.2, 0.4)
DELAY_DICE_CONFIRM = 0.3
DELAY_DICE_LAST_NORMAL = 0.5
DELAY_DICE_LAST_TENSE = (1.5, 2.5)
DELAY_DICE_SPIN_INTERVAL = 0.05
DELAY_DICE_SPIN_DURATION = 1.0

# =============================================================================
# DICE LOGIC
# =============================================================================

class DiceResult:
    """Represents the result of a chinchiro roll."""
    
    HIFUMI = "HIFUMI"
    SHIGORO = "SHIGORO"
    PINZORO = "PINZORO"
    ARASHI = "ARASHI"
    ME = "ME"
    MENASHI = "MENASHI"
    
    def __init__(self, dice: list[int]):
        self.dice = sorted(dice)
        self.role, self.value, self.multiplier = self._evaluate()
    
    def _evaluate(self) -> tuple[str, int, int]:
        d = self.dice
        
        # Hifumi (1-2-3): auto lose x2
        if d == [1, 2, 3]:
            return (self.HIFUMI, 0, -2)
        
        # Shigoro (4-5-6): auto win x2
        if d == [4, 5, 6]:
            return (self.SHIGORO, 7, 2)
        
        # Pinzoro (1-1-1): best, x5
        if d == [1, 1, 1]:
            return (self.PINZORO, 10, 5)
        
        # Arashi (triplets): x3
        if d[0] == d[1] == d[2]:
            return (self.ARASHI, d[0] + 3, 3)  # value: 4-9 for display
        
        # Me (pair + different): value is the odd one
        if d[0] == d[1]:
            return (self.ME, d[2], 1)
        if d[1] == d[2]:
            return (self.ME, d[0], 1)
        
        # Menashi (no valid combination)
        return (self.MENASHI, 0, 0)
    
    def is_valid(self) -> bool:
        return self.role != self.MENASHI
    
    def beats(self, other: "DiceResult") -> int:
        """Returns 1 if self wins, -1 if other wins, 0 if tie."""
        if self.value > other.value:
            return 1
        elif self.value < other.value:
            return -1
        return 0


def roll_dice() -> list[int]:
    """Roll 3 dice."""
    return [random.randint(1, 6) for _ in range(3)]


def is_tense_situation(confirmed: list[int], pending: int) -> bool:
    """Check if the current situation is tense (potential good/bad role)."""
    if len(confirmed) < 2:
        return False
    
    c = sorted(confirmed)
    
    # Potential Arashi
    if c[0] == c[1]:
        return True
    
    # Potential Shigoro
    if set(c).issubset({4, 5, 6}):
        return True
    
    # Potential Hifumi
    if set(c).issubset({1, 2, 3}):
        return True
    
    return False


# =============================================================================
# DISPLAY
# =============================================================================

def get_width() -> int:
    """Get terminal width, minimum 60."""
    return max(shutil.get_terminal_size().columns, 60)


def log_line(text: str) -> str:
    """Format a log line."""
    return text


def log_delay(heavy: bool = False):
    """Sleep with jitter for realistic log feel."""
    if heavy:
        base = random.uniform(*DELAY_HEAVY)
    else:
        base = DELAY_BASE
    jitter = random.uniform(*DELAY_JITTER)
    time.sleep(max(0.01, base + jitter))


def print_log(text: str, heavy: bool = False):
    """Print a log line with delay."""
    log_delay(heavy)
    print(text)


def timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def animate_dice_roll(final_dice: list[int]) -> None:
    """Animate the dice roll with progressive reveal."""
    width = get_width()
    prefix = "[PROC] ROLLING... "
    
    # Phase 1: All spinning
    end_time = time.time() + DELAY_DICE_SPIN_DURATION
    while time.time() < end_time:
        display = [f"{random.randint(1,6):02d}" for _ in range(3)]
        line = f"{prefix}[{display[0]} {display[1]} {display[2]}]"
        sys.stdout.write(f"\r{line:<{width}}")
        sys.stdout.flush()
        time.sleep(DELAY_DICE_SPIN_INTERVAL)
    
    # Phase 2: Reveal one by one
    confirmed = []
    for i, val in enumerate(final_dice):
        confirmed.append(f"{val:02d}")
        remaining = 3 - len(confirmed)
        
        # Determine delay for this confirmation
        if i == 2:  # Last dice
            if is_tense_situation(final_dice[:2], final_dice[2]):
                delay = random.uniform(*DELAY_DICE_LAST_TENSE)
            else:
                delay = DELAY_DICE_LAST_NORMAL
        else:
            delay = DELAY_DICE_CONFIRM
        
        # Spin remaining dice during delay
        end_time = time.time() + delay
        while time.time() < end_time:
            spinning = [f"{random.randint(1,6):02d}" for _ in range(remaining)]
            all_dice = confirmed + spinning
            line = f"{prefix}[{all_dice[0]} {all_dice[1]} {all_dice[2]}]"
            sys.stdout.write(f"\r{line:<{width}}")
            sys.stdout.flush()
            time.sleep(DELAY_DICE_SPIN_INTERVAL)
        
        # Show confirmed state
        spinning = ["##" for _ in range(remaining)]
        all_dice = confirmed + spinning
        line = f"{prefix}[{all_dice[0]} {all_dice[1]} {all_dice[2]}]"
        sys.stdout.write(f"\r{line:<{width}}")
        sys.stdout.flush()
    
    print()  # Newline after animation


def format_result(result: DiceResult) -> str:
    """Format dice result for display."""
    d = result.dice
    dice_str = f"{d[0]}-{d[1]}-{d[2]}"
    
    if result.role == DiceResult.MENASHI:
        return f"{dice_str} {result.role}"
    
    mult_str = f"x{abs(result.multiplier)}"
    
    if result.multiplier < 0:
        return f"{dice_str} {result.role} {mult_str} LOSS"
    elif result.role in (DiceResult.SHIGORO, DiceResult.PINZORO, DiceResult.ARASHI):
        return f"{dice_str} {result.role} {mult_str} WIN"
    else:
        return f"{dice_str} {result.role}:{result.value} {mult_str}"


# =============================================================================
# GAME
# =============================================================================

class Game:
    def __init__(self, player: Player):
        self.player = player
        self.round = 0
        self.running = True
        self.auto_bet = 0  # 0 = manual mode
    
    def print_header(self):
        print_log(f"[{timestamp()}] DICE_ANALYZER v{VERSION} | SESSION {SESSION_ID} | ROUND {self.round:03d}")
    
    def print_status(self, pot: int = 0):
        line = f"[STATUS] BANKROLL: {self.player.bankroll:,}"
        if pot:
            line += f" | POT: {pot:,}"
        print_log(line)
    
    def get_bet(self) -> int:
        """Get bet amount from player. Returns 0 to quit."""
        log_delay(heavy=True)
        
        # Auto mode
        if self.auto_bet > 0:
            bet = min(self.auto_bet, self.player.bankroll)
            sys.stdout.write(f"[INPUT] BET_AMOUNT AUTO: {bet:,} (ENTER to interrupt) > ")
            sys.stdout.flush()
            
            # Wait 2 seconds for interrupt
            import select
            if select.select([sys.stdin], [], [], 2.0)[0]:
                line = sys.stdin.readline().strip()
                # Any input (including just Enter) interrupts auto mode
                self.auto_bet = 0
                print_log("[INFO] AUTO_MODE_DISABLED")
                if line:
                    return self._parse_bet_input(line)
                # Empty enter = go to manual input
                sys.stdout.write(f"[INPUT] BET_AMOUNT (1-{self.player.bankroll:,}) > ")
                sys.stdout.flush()
                line = input().strip()
                return self._parse_bet_input(line)
            print()  # Newline after timeout
            return bet
        
        # Manual mode
        sys.stdout.write(f"[INPUT] BET_AMOUNT (1-{self.player.bankroll:,}) > ")
        sys.stdout.flush()
        line = input().strip()
        return self._parse_bet_input(line)
    
    def _parse_bet_input(self, line: str) -> int:
        """Parse bet input. Returns bet amount, 0 for quit, -1 for invalid."""
        line = line.lower().strip()
        
        if line in ('q', 'quit', 'exit', '0'):
            return 0
        
        # Check for auto mode
        parts = line.split()
        if len(parts) == 2 and parts[1] == 'auto':
            try:
                bet = int(parts[0].replace(',', ''))
                if 1 <= bet <= self.player.bankroll:
                    self.auto_bet = bet
                    print_log(f"[INFO] AUTO_MODE_ENABLED: {bet:,}")
                    return bet
            except ValueError:
                pass
            return -1
        
        # Normal bet
        try:
            bet = int(line.replace(',', ''))
            if 1 <= bet <= self.player.bankroll:
                return bet
            print_log("[ERROR] INVALID_AMOUNT: OUT_OF_RANGE")
            return -1
        except ValueError:
            print_log("[ERROR] INVALID_AMOUNT: NOT_A_NUMBER")
            return -1
    
    def _confirm_quit(self) -> bool:
        """Confirm quit. Returns True if user wants to quit."""
        sys.stdout.write("[INPUT] QUIT_SESSION [Y/n] > ")
        sys.stdout.flush()
        response = input().strip().lower()
        return response != 'n'
    
    def player_roll(self, max_attempts: int = 3) -> DiceResult | None:
        """Roll for player with up to max_attempts."""
        for attempt in range(max_attempts):
            dice = roll_dice()
            animate_dice_roll(dice)
            result = DiceResult(dice)
            
            if result.is_valid():
                return result
            
            if attempt < max_attempts - 1:
                print_log(f"[RESULT] {format_result(result)} | REROLL {attempt + 2}/{max_attempts}")
            else:
                print_log(f"[RESULT] {format_result(result)} | NO_VALID_ROLL")
        
        return None
    
    def dealer_roll(self, max_attempts: int = 3) -> DiceResult | None:
        """Roll for dealer."""
        print_log("[PROC] DEALER_ROLL_SEQUENCE", heavy=True)
        for attempt in range(max_attempts):
            dice = roll_dice()
            animate_dice_roll(dice)
            result = DiceResult(dice)
            
            if result.is_valid():
                return result
            
            if attempt < max_attempts - 1:
                print_log(f"[DEALER] {format_result(result)} | REROLL {attempt + 2}/{max_attempts}")
        
        return None
    
    def resolve_round(self, player_result: DiceResult, dealer_result: DiceResult | None, bet: int) -> int:
        """Resolve round and return payout (can be negative)."""
        
        # Player has auto-lose (Hifumi)
        if player_result.role == DiceResult.HIFUMI:
            return -bet * abs(player_result.multiplier)
        
        # Player has auto-win (Shigoro, Pinzoro, Arashi)
        if player_result.role in (DiceResult.SHIGORO, DiceResult.PINZORO, DiceResult.ARASHI):
            return bet * player_result.multiplier
        
        # Dealer couldn't get valid roll - player wins
        if dealer_result is None:
            return bet * player_result.multiplier
        
        # Dealer has auto-lose
        if dealer_result.role == DiceResult.HIFUMI:
            return bet * player_result.multiplier
        
        # Dealer has auto-win
        if dealer_result.role in (DiceResult.SHIGORO, DiceResult.PINZORO, DiceResult.ARASHI):
            return -bet * dealer_result.multiplier
        
        # Compare values
        comparison = player_result.beats(dealer_result)
        if comparison > 0:
            return bet * player_result.multiplier
        elif comparison < 0:
            return -bet * dealer_result.multiplier
        
        # Tie - return bet
        return 0
    
    def play_round(self):
        """Play a single round."""
        self.round += 1
        print()
        self.print_header()
        self.print_status()
        
        # Get bet
        bet = self.get_bet()
        while bet == -1:  # Invalid input, retry
            bet = self.get_bet()
        
        if bet == 0:
            if not self._confirm_quit():
                return
            print_log("[INFO] SESSION_TERMINATED_BY_USER")
            self.running = False
            return
        
        self.print_status(pot=bet)
        
        # Player roll
        print_log("[PROC] PLAYER_ROLL_SEQUENCE", heavy=True)
        player_result = self.player_roll()
        
        if player_result is None:
            # No valid roll - lose bet
            payout = -bet
            print_log(f"[RESULT] NO_VALID_COMBINATION | DEBIT: {payout:,}")
        elif player_result.role == DiceResult.HIFUMI:
            # Auto lose
            payout = -bet * abs(player_result.multiplier)
            print_log(f"[RESULT] {format_result(player_result)} | DEBIT: {payout:,}")
        elif player_result.role in (DiceResult.SHIGORO, DiceResult.PINZORO, DiceResult.ARASHI):
            # Auto win
            payout = bet * player_result.multiplier
            print_log(f"[RESULT] {format_result(player_result)} | CREDIT: +{payout:,}")
        else:
            # Need dealer roll
            print_log(f"[RESULT] {format_result(player_result)} | AWAIT_DEALER")
            dealer_result = self.dealer_roll()
            
            if dealer_result:
                print_log(f"[DEALER] {format_result(dealer_result)}")
            
            payout = self.resolve_round(player_result, dealer_result, bet)
            
            if payout > 0:
                print_log(f"[TRANSACTION] PLAYER_WIN | CREDIT: +{payout:,}")
            elif payout < 0:
                print_log(f"[TRANSACTION] DEALER_WIN | DEBIT: {payout:,}")
            else:
                print_log(f"[TRANSACTION] DRAW | NO_CHANGE")
        
        # Update bankroll
        self.player.bankroll += payout
        self.print_status()
        
        # Check bankruptcy
        if self.player.bankroll <= 0:
            print_log("[FATAL] BANKROLL_DEPLETED | SESSION_TERMINATED")
            self.running = False
            return
    
    def run(self):
        """Main game loop."""
        print_log(f"[{timestamp()}] DICE_ANALYZER v{VERSION} INITIALIZED")
        print_log(f"[INFO] SESSION_ID: {SESSION_ID}")
        print_log(f"[INFO] INITIAL_BANKROLL: {self.player.bankroll:,}")
        print_log("[INFO] COMMANDS: <amount> | <amount> auto | 0/q to quit")
        
        while self.running:
            self.play_round()
        
        print()
        print_log(f"[{timestamp()}] SESSION_COMPLETE")
        print_log(f"[SUMMARY] ROUNDS_PLAYED: {self.round}")
        print_log(f"[SUMMARY] FINAL_BANKROLL: {self.player.bankroll:,}")
        pnl = self.player.bankroll - INITIAL_BANKROLL
        pnl_str = f"+{pnl:,}" if pnl >= 0 else f"{pnl:,}"
        print_log(f"[SUMMARY] NET_PNL: {pnl_str}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    player = HumanPlayer("OPERATOR", INITIAL_BANKROLL)
    game = Game(player)
    
    try:
        game.run()
    except KeyboardInterrupt:
        print()
        print_log("[WARN] INTERRUPT_RECEIVED")
        print_log(f"[{timestamp()}] SESSION_ABORTED")


if __name__ == "__main__":
    main()
