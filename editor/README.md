# ICE Gauntlet map editor

Los mapas en ICE Gauntlet consisten en una matriz bidimensional de hasta 128x128 celdas. Una celda es del tamaño de un jugador y puede estar vacía, contener un objeto o ser una pared.

Estas matrices se pueden crear con un editor de texto plano aunque se recomienda utilizar algún prograama para su creación, como por ejemplo **Tiled**.

## Crear un mapa con Tiled

Se adjunta un fichero de plantilla para *Tiled* llamado *template.tmx*. Este fichero a su vez necesita de un conjunto de *tiles* o *tileset*, los utilizados por *ICE Gauntlet* se pueden encontrar en el archivo *map_tiles.tsx*.

Así pues comenzamos por copiar el template a otro archivo para su posterior modificación:
```sh
cp template.tmx my_map.tmx
```

Y ahora abrimos el fichero *my_map.tmx* con *Tiled* para crear el mapa que deseemos. Para que el mapa pueda ser utilizado debe contar al menos con un inicio (o zona de *spawn*) y una salida (o *EXIT*). Los elementos que se pueden utilizar en el mapa se muestran a continuación:

|Elemento|Icono|
|--------|-----|
|Paredes|![walls](doc/walls.png)|
|Puertas|![doors](doc/doors.png)|
|Inicio|![spawn](doc/default_spawn.png)|
|Inicio guerrero|![warrior spawn](doc/warrior_spawn.png)|
|Inicio valkiria|![valkyrie spawn](doc/valkyrie_spawn.png)|
|Inicio mago|![wizard spawn](doc/wizard_spawn.png)|
|Inicio elfo|![elf spawn](doc/elf_spawn.png)|
|Salida|![exit](doc/exit.png)|
|Teletransportador|![teleport](doc/teleport.png)|
|Llave|![key](doc/key.png)|
|Tesoro|![treasure](doc/treasure.png)|
|Comida pequeña|![small food](doc/small_food.png)|
|Comida grande|![big food](doc/big_food.png)|

Se recomienda que al mapa cuente con tantas llaves como sea necesario para alcanzar la salida.

## Convertir archivos TMX a JSON

El formato de archivos que consume el motor es *json*, por tanto antes de usar un mapa creado con *Tiled* tendremos que convertilo a un formato adecuado. Para ello utilizaremos *tiled2json*. Además, hay que traducir los identificadores utilizados por *Tiled* en identificadores válidos para *ICE Gauntlet*. Esta traducción la realiza automáticamente *tiled2json* si se le especifica un archivo de traducción válido. Este archivo consistirá en un diccionario *clave-valor*, siendo la *clave* el identificador usado por *Tiled* y el *valor* el identificador que utiliza *ICE Gauntlet*. Se incluye el fichero *schematic2tileid.json* que está preparado para utilizarlo con *map_tiles.tsx*.

Para convertir el fichero y traducir los identificadores de celda ejecutamos el siguiente comando:

```sh
./tiled2json -t schematic2tileid.json my_map.tmx
```

Este comando escribe en la salida estándar el mapa convertido a json, se puede redirigir la salida a un fichero o símplemente utilizar la opcion *--output* o *-o* para indicar un fichero de salida:

```sh
./tiled2json -t schematic2tileid.json -o my_map.json my_map.tmx
```

Por último, podremos poner un nombre al mapa utilizando *--name*:

```sh
./tiled2json -t schematic2tileid.json --name "My first map" -o my_map.json my_map.tmx
```

## Otras opciones de conversión

El tamaño máximo de un mapa es de 128x128 celdas, que es el tamaño del mapa en *template.tmx*. Sin embargo un mapa no tiene porqué ocupar dicha extensión, normalmente ocupará menos celdas. Por defecto *tiled2json* ajusta el tamaño del mapa resultante al mínimo necesario para almacenar todas las celdas que tienen algún elemento, por tanto podrá crear mapas de cualquier tamaño siempre que sean menores de 128x128. Se puede desactivar este ajuste para que genere un mapa del mismo tamaño que el fichero *TMX* (pero nunca de más del máximo admitido) utilizando la opción *--full-map* o símplemente *-f*.

En *Tiled* se puede establecer una celda como *vacía*, también se puede dejar celdas sin un valor asociado. Estos dos estados de una celda son diferentes en *Tiled*, sin embargo para *ICE Gauntlet* es lo mismo que una celda no tenga nada o tenga asociado el identificador "vacío". Esto se consigue al convertir el mapa utilizando el mismo identificador de salida en ambos casos. Sin embargo se puede indicar en la conversión un valor diferente para todas las celdas sin valor definido, esto se indica con la opción *--null-blocks* o *-n* seguida del valor a utilizar para estas celdas.

Por último, cuando se está convirtiendo un mapa, *tiled2json* verifica que el valor de la celda es válido, de manera que si encuentra un identificador de celda que no pueda traducir o de un elemento no implementado en el juego, se informará por pantalla de la posición de la celda y el valor que ha provocado el error, cancelando la conversión. Sin embargo se puede indicar al conversor que ignore estas celdas y continue la conversión. Símplemente con añadir la opción *--force* se ignorarán los valores no soportados (dejándolos vacíos en el mapa destino).

## Probar el nuevo mapa

Una vez hemos convertido el mapa podremos probarlo con la versión *local* del programa. Para ello debemos copiar el *json* generado en alguna de estas rutas:
* $PWD/assets
* $HOME/.icegauntlet/assets
* /usr/local/share/icegauntlet/assets
* /usr/share/icegauntlet/assets

Y ejecutamos *dungeon_local* con el nombre del fichero de nuestro nuevo mapa:

```sh
dungeon_local my_map.json
```
