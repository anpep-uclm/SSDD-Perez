# ICE Gauntlet

ICE Gauntlet es un juego en red educativo que pretende introducir en el diseño de sistemas distribuídos.

El juego está basado en el clásico de Atari Games: GAUNTLET, pero mucho más simple ya que el objetivo del programa es meramente educativo, animamos a colaborar con el proyecto para añadir más features a quien así lo desee.

## Python y ZeroC ICE

El lenguaje utilizado para su desarrollo ha sido **Python 3** con las siguientes librerías externas:
* Pyxel
* Pillow

y opcionalmente:
* xmltodict

Como motor de red (middleware de comunicaciones) se ha utilizado ZeroC ICE 3.7.4 aunque debería funcionar con cualquier versión, al menos desde **ICE 3.5**.

## Instalación

Se recomienda la instalación del proyecto en un *virtual environment* dedicado. Se puede utilizar el fichero *requetiments.txt* para construír dicho entorno:
```sh
mkvirtualenv icegauntlet -p /usr/bin/python3
pip install -r requeriments.txt
```
Finalmente la instalación se puede realizar como cualquier otro proyecto estándar de Python:
```sh
python3 setup.py install
```

## Ejecución en local

Para probar mapas o el propio motor del juego, se puede ejecutar en local sin necesidad de conectar a un servidor, símplemente ejecutamos *dungeon_local* y el mapa que queramos cargar:
```sh
dungeon_local tutorial.json
```

Los mapas se buscan en las carpetas de *assets* del juego, es decir, cualquiera de las siguientes:
* $PWD/assets
* $HOME/.icegauntlet/assets
* /usr/local/share/icegauntlet/assets
* /usr/share/icegauntlet/assets

Además podemos indicar varios mapas que se jugarán en el mismo orden en el que se especifican:
```sh
dungeon_local tutorial.json level01.json level02.json
```

Por defecto el personaje seleccionado es el guerrero (*warrior*) pero puede elegirse cualquiera de los cuatro tipos disponibles: guerrero(*warrior*), valkiria (*valkyrie*), mago (*wizard*) y elfo(*elf*). Para ello usaremos la opción *--player* o símplemente *-p*:
```sh
dungeon_local -p elf tutorial.json
```
