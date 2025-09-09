#!/bin/bash
# ============================
# Script de mise à jour des fichiers .ics
# ============================

# Répertoire du script (où seront stockés les .ics)
SCRIPT_DIR="$(dirname "$(realpath "$0")")"

# Table correspondance: URL -> fichier local
declare -A ICS_FILES=(
  ["https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=6579&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8"]="edt1.ics"
  ["https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=6581&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8"]="edt2.ics"
  ["https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=3911&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8"]="edt3.ics"
  ["https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=3930&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8"]="ang.ics"
  ["https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=3957&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8"]="msh1.ics"
  ["https://edt-consult.univ-eiffel.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=3941&projectId=1&calType=ical&nbWeeks=12&displayConfigId=8"]="msh2.ics"
)

# Téléchargement
for URL in "${!ICS_FILES[@]}"; do
    FILE="${ICS_FILES[$URL]}"
    DEST="$SCRIPT_DIR/$FILE"
    echo "Mise à jour de $FILE ..."
    curl -s -L "$URL" -o "$DEST"
    if [ $? -eq 0 ]; then
        echo " → $FILE mis à jour"
    else
        echo " ⚠️ Erreur lors du téléchargement de $URL"
    fi
done
