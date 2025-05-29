# 🔔 Crypto Signal Bot – Public Repo Edition

Bot de signaux techniques (EMA/RSI + actu optionnelle) qui envoie une alerte Telegram
toutes les 15 minutes via GitHub Actions. Aucun ordre n'est exécuté automatiquement.

## ⚙️ Configuration

1. Fork ce dépôt en mode **public**
2. Va dans `Settings > Secrets and variables > Actions` → ajoute :
   - `TG_TOKEN` = token de ton bot Telegram (via @BotFather)
   - `TG_CHAT_ID` = identifiant du canal ou groupe
   - `CP_KEY` = (optionnel) clé API gratuite depuis https://cryptopanic.com
3. Pousse une fois → les signaux s'exécuteront automatiquement toutes les 15 min

## 🧪 Indicateurs utilisés

- EMA 20 / EMA 50 : croisement de tendance
- RSI 14 : entrée < 30, sortie > 70
- Filtre actu : évite les signaux quand sentiment ≈ panique

## ✅ Gratuit et sécurisé

- Dépôt **public** → GitHub Actions gratuit illimité
- Clés cachées dans les **Secrets GitHub**
- Pas d'exécution automatique : vous gardez le contrôle

## ✨ Exemples d'alerte
```
BUY BTC/USDT
Prix : 26850.00
RSI : 29.1
2025-05-29 12:00 UTC
```

👨‍💻 Basé sur Python 3.11, `ccxt`, `pandas_ta`, `requests`.
