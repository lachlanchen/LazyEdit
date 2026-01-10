<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

<p>
  <b>Languages:</b>
  <a href="../README.md">English</a>
  · <a href="README.zh-Hant.md">中文（繁體）</a>
  · <a href="README.zh-Hans.md">中文 (简体)</a>
  · <a href="README.ja.md">日本語</a>
  · <a href="README.ko.md">한국어</a>
  · <a href="README.vi.md">Tiếng Việt</a>
  · <a href="README.ar.md">العربية</a>
  · <a href="README.fr.md">Français</a>
  · <a href="README.es.md">Español</a>
</p>

# LazyEdit

LazyEdit est un outil d’édition vidéo automatique alimenté par l’IA. Il génère des sous-titres, des temps forts, des cartes de mots et des métadonnées de qualité professionnelle pour automatiser les tâches fastidieuses.

## Fonctionnalités

- **Transcription automatique** : transcription audio via IA
- **Captioning automatique** : descriptions du contenu vidéo
- **Sous-titres automatiques** : création et incrustation directe
- **Mise en évidence** : surlignage des mots clés
- **Métadonnées automatiques** : extraction et génération
- **Cartes de vocabulaire** : cartes éducatives pour l’apprentissage
- **Génération de teaser** : répétition de segments clés au début
- **Support multilingue** : plusieurs langues dont anglais et chinois
- **Génération de couverture** : capture d’un meilleur frame avec overlay

## Installation

### Prérequis

- Python 3.10 ou plus
- FFmpeg
- GPU compatible CUDA (accélération de transcription)
- Gestionnaire d’environnements Conda

### Étapes d’installation

1. Cloner le dépôt :
   ```bash
   git clone <repository_url>
   cd lazyedit
   ```

2. Exécuter le script d’installation :
   ```bash
   chmod +x install_lazyedit.sh
   ./install_lazyedit.sh
   ```

Le script :
- Installe les paquets système requis (ffmpeg, tmux)
- Crée un environnement conda nommé "lazyedit"
- Configure le service systemd pour le démarrage automatique
- Configure les permissions nécessaires

## Utilisation

LazyEdit fonctionne comme une application web accessible sur http://localhost:8081

### Traiter une vidéo

1. Téléverser la vidéo via l’interface web
2. LazyEdit effectuera automatiquement :
   - Transcription et captioning
   - Génération de métadonnées et de contenu pédagogique
   - Sous-titres dans la langue détectée
   - Mise en évidence des termes importants
   - Création d’un teaser
   - Génération d’une image de couverture
   - Packaging et retour des résultats

### Ligne de commande

```bash
conda activate lazyedit
cd /path/to/lazyedit
python app.py -m lazyedit
```

## Structure du projet

- `app.py` - point d’entrée principal
- `lazyedit/` - modules principaux
  - `autocut_processor.py` - segmentation et transcription
  - `subtitle_metadata.py` - génération de métadonnées
  - `subtitle_translate.py` - traduction de sous-titres
  - `video_captioner.py` - captioning vidéo
  - `words_card.py` - cartes de vocabulaire
  - `utils.py` - utilitaires
  - `openai_version_check.py` - compatibilité API OpenAI

## Configuration

La configuration systemd est créée dans `/etc/systemd/system/lazyedit.service`.

LazyEdit s’exécute dans une session tmux nommée "lazyedit" pour rester en arrière-plan.

## Gestion du service

- Démarrer : `sudo systemctl start lazyedit.service`
- Arrêter : `sudo systemctl stop lazyedit.service`
- Statut : `sudo systemctl status lazyedit.service`
- Logs : `sudo journalctl -u lazyedit.service`

## Utilisation avancée

Personnalisations possibles :
- Durée et position du teaser
- Styles de mise en évidence
- Police et position des sous-titres
- Structure des dossiers de sortie
- Sélection du GPU

## Dépannage

- Si l’application ne démarre pas, vérifier systemd et les logs
- En cas d’échec, vérifier l’installation de FFmpeg
- Pour GPU, vérifier CUDA et disponibilité du GPU
- S’assurer que l’environnement conda est activé

## Licence

[Indiquez la licence ici]

## Remerciements

LazyEdit utilise :
- FFmpeg (traitement vidéo)
- Modèles OpenAI (IA)
- Tornado (framework web)
- MoviePy (montage vidéo)
- CJKWrap (texte multilingue)
