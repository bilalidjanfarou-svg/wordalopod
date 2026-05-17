from wonderwords import RandomWord

# ── Fonctions principales ────────────────────────────────────────────────────

def choose_secret_word(word_length):
    w = RandomWord()
    return w.word(word_min_length=word_length, word_max_length=word_length)

def get_player_guess(word_list, num_letters):
    while True:
        guess = input("✏️  Votre mot : ").lower().strip()
        if len(guess) == num_letters and guess in word_list:
            return guess
        elif len(guess) != num_letters:
            print(f"   ⚠️  Le mot doit contenir exactement {num_letters} lettres.")
        else:
            print(f"   ⚠️  « {guess} » n'est pas dans la liste de mots valides.")

def get_letter_colors(guess, secret_word):
    guess_list  = list(guess)
    secret_list = list(secret_word)
    colors = []
    i = 0
    while i < len(guess_list):
        if guess_list[i] == secret_list[i]:
            colors.append("green")
            secret_list[i] = "*"
        else:
            colors.append("gray")
        i += 1
    i = 0
    while i < len(guess_list):
        if colors[i] == "gray" and guess_list[i] in secret_list:
            colors[i] = "yellow"
            secret_list[secret_list.index(guess_list[i])] = "*"
        i += 1
    return colors

# ── AMÉLIORATION 1 : emojis personnalisés ───────────────────────────────────
COLOR_EMOJI = {
    "green":  "🟦",   # bleu  = bonne lettre, bonne position
    "yellow": "🟧",   # orange = bonne lettre, mauvaise position
    "gray":   "⬜",   # blanc = lettre absente
}

# ── AMÉLIORATION 3 : affichage du clavier ───────────────────────────────────
def display_keyboard(used_colors):
    """Affiche les lettres de l'alphabet avec leur statut coloré."""
    rows = ["azertyuiop", "qsdfghjklm", "wxcvbn"]
    print("\n  🎹 Clavier :")
    for row in rows:
        line = "  "
        for letter in row:
            if used_colors.get(letter) == "green":
                line += f"🟦{letter} "
            elif used_colors.get(letter) == "yellow":
                line += f"🟧{letter} "
            elif used_colors.get(letter) == "gray":
                line += f"⬜{letter} "
            else:
                line += f"  {letter} "   # lettre non encore utilisée
        print(line)

def display_board(guess_list, color_list, word_len, max_attempts, used_colors):
    attempts_left = max_attempts - len(guess_list)
    print(f"\n{'─'*30}")
    print(f"  🎮 Wordalopod  —  {len(guess_list)}/{max_attempts} tentatives")
    print(f"{'─'*30}")

    i = 0
    while i < len(guess_list):
        letters = " ".join(guess_list[i].upper())
        emojis  = " ".join(COLOR_EMOJI[c] for c in color_list[i])
        print(f"  {letters}")
        print(f"  {emojis}")
        print()
        i += 1

    j = 0
    while j < attempts_left:
        print("  " + "─  " * word_len)
        j += 1

    display_keyboard(used_colors)

# ── AMÉLIORATION 2 : mode 2 joueurs avec tableau de scores ──────────────────
def update_scores(scores, player_name, attempts_used):
    """Ajoute les points du tour au tableau de scores (moins de tentatives = plus de points)."""
    if attempts_used > 0:
        points = max(0, 100 - (attempts_used - 1) * 15)
    else:
        points = 0
    scores[player_name] = scores.get(player_name, 0) + points
    return points

def display_scores(scores):
    print("\n  🏆 Tableau des scores :")
    for name, score in sorted(scores.items(), key=lambda x: -x[1]):
        print(f"     {name} : {score} pts")

# ── Fonction principale ──────────────────────────────────────────────────────
def play_game():
    num_letters  = 5
    max_attempts = 6
    scores       = {}

    # ── Mode 2 joueurs ─────────────────────────────────────────────────────
    print("=" * 35)
    print("   🟦 Bienvenue sur Wordalopod ! 🟦")
    print("=" * 35)
    while True:
        choix = input("\nNombre de joueurs ? (1 ou 2) : ").strip()
        if choix in ("1", "2"):
            num_players = int(choix)
            break
    print("⚠️  Entrez 1 ou 2.")
    players = []
    for i in range(num_players):
        name = input(f"Nom du joueur {i+1} : ").strip() or f"Joueur {i+1}"
        players.append(name)
        scores[name] = 0

    all_words   = RandomWord()
    word_list   = all_words.filter(word_min_length=num_letters, word_max_length=num_letters)

    play_again = True
    while play_again:
        for current_player in players:
            print(f"\n\n  🎯 Tour de {current_player} !")

            # En mode 2 joueurs, le 2ème joueur choisit le mot secret
            if num_players == 2:
                other = [p for p in players if p != current_player][0]
                print(f"  {other}, entrez le mot secret (5 lettres) :")
                while True:
                    secret = input("  → ").lower().strip()
                    if len(secret) == num_letters and secret in word_list:
                        break
                    print(f"  ⚠️  Mot invalide. Entrez un mot de {num_letters} lettres.")
                print("\033[8m", end="")   # cacher le texte (terminal supportant ANSI)
            else:
                secret = choose_secret_word(num_letters)

            guess_list  = []
            color_list  = []
            used_colors = {}   # lettre → meilleure couleur vue jusqu'ici

            won = False

            while len(guess_list) < max_attempts:
                print(f"\n  Devinez le mot ({num_letters} lettres) !")
                guess  = get_player_guess(word_list, num_letters)
                colors = get_letter_colors(guess, secret)

                guess_list.append(guess)
                color_list.append(colors)

                # Mettre à jour le clavier (garder la meilleure couleur)
                priority = {"green": 3, "yellow": 2, "gray": 1}
                for letter, color in zip(guess, colors):
                    if priority[color] > priority.get(used_colors.get(letter, "gray"), 0):
                        used_colors[letter] = color

                display_board(guess_list, color_list, num_letters, max_attempts, used_colors)

                if guess == secret:
                    won = True
                    break

            # Résultat du tour
            if won:
                pts = update_scores(scores, current_player, len(guess_list))
                print(f"\n  🎉 Bravo {current_player} ! Mot trouvé en {len(guess_list)} tentative(s) → +{pts} pts")
            else:
                update_scores(scores, current_player, 0)
                print(f"\n  😞 Perdu ! Le mot secret était « {secret.upper()} ».")

        display_scores(scores)

        rejouer = input("\n  Rejouer ? (o/n) : ").strip().lower()
        play_again = rejouer == "o"

    print("\n  Merci d'avoir joué ! À bientôt 👋\n")

# ── Lancement ────────────────────────────────────────────────────────────────
play_game()