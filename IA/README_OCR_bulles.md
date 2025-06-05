OCR bulles

Pour lancer:
```pip install -r requirements.txt```

Egalement installer tesseract

Pour utiliser le script, appeler la fonction:
```get_texts(path_image,boxes)```

path_image -> chemin vers l'image
boxes -> tableau de tableau contenant les coordonées a format yolo8
exemple: 

boxes = [
    [0.44609375, 0.11484375, 0.2265625, 0.12734375],
    [0.86328125, 0.14921875, 0.225, 0.11015625],
    [0.39140625, 0.303125, 0.1828125, 0.10546875]
]