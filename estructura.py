import os

def imprimir_estructura(ruta, nivel=0):
    # Si la carpeta actual es "env", se omite
    if os.path.basename(ruta) == "env":
        return

    prefijo = "    " * nivel
    print(f"{prefijo}{os.path.basename(ruta)}/")
    
    try:
        entradas = os.listdir(ruta)
    except PermissionError:
        print(f"{prefijo}    [Permiso denegado]")
        return

    for entrada in sorted(entradas):
        ruta_completa = os.path.join(ruta, entrada)
        if os.path.isdir(ruta_completa):
            # Omitir subcarpeta "env"
            if entrada.lower() == "env":
                continue
            imprimir_estructura(ruta_completa, nivel + 1)
        else:
            print(f"{prefijo}    {entrada}")

if __name__ == "__main__":
    ruta_directorio = input("Ingrese la ruta de la carpeta: ").strip()
    if os.path.isdir(ruta_directorio):
        imprimir_estructura(ruta_directorio)
    else:
        print("La ruta proporcionada no es una carpeta válida.")


# Estructura:


# .vscode/
#     launch.json
# Guiones/
#     script.txt
# Videos/
#     Horizontal/
#     Vertical/
# Videosm/
# __pycache__/
#     config.cpython-312.pyc
# config.py
# estructura.py
# main.py
# media/
#     Caps/
#         BetaH/
#         BetaV/
#     Fuentes Letra/
#         Nanum_Gothic.zip
#     Transiciones/
#         DALL·E 2024-06-15 16.32.07 - A whimsical and colorful wallpaper design with feathers, stars, and hearts. The background is a soft pastel color, creating a dreamy and playful atmos.webp
#         DALL·E 2024-06-15 18.32.55 - An abstract wallpaper design inspired by the provided image, featuring a gradient background with flowing shapes and patterns in warm, sunset-like col.webp
#         DALL·E 2024-06-15 18.35.55 - A vibrant and colorful painting of a white coffee cup with a galaxy inside. The galaxy inside the cup features swirling stars, planets, and cosmic dus.webp
#         DALL·E 2024-06-15 18.40.46 - A surrealist painting of a coffee cup with a penguin on an iceberg inside. The penguin is standing on the iceberg, floating in a sea of coffee inside .webp
#         DALL·E 2024-06-15 18.42.43 - A surrealist painting of a coffee cup with an office chair on a desk inside. The office chair is positioned on top of the desk, which is floating in a.webp
#         DALL·E 2024-06-15 18.49.42 - A top-down view of a cup of coffee in a vibrant, colorful artistic style similar to a painting of fried eggs. The coffee is dark brown with the foam o.webp
#         DALL·E 2024-06-15 18.52.24 - A top-down view of a cup of coffee in a vibrant, colorful artistic style similar to a painting of fried eggs. The coffee is dark brown with the foam o.webp
#         DALL·E 2024-06-15 18.53.21 - A vibrant, colorful artistic style image of a mountain made up of numerous coffee cups. The cups are stacked and scattered in a dynamic, chaotic arran.webp
#         DALL·E 2024-06-15 18.55.11 - A vibrant, colorful anime style image of a mountain made up of numerous coffee cups. The cups are stacked and scattered in a dynamic, whimsical arrang.webp
#         DALL·E 2024-06-15 18.57.25 - A vibrant and action-packed shonen anime style image featuring a single anthropomorphic coffee mug as the main character. The coffee mug has a dynamic.webp
#         DALL·E 2024-06-15 18.58.27 - A dark and intense anime style image featuring a single anthropomorphic coffee mug as the main character, in the style of Berserk. The coffee mug has .webp
#         DALL·E 2024-06-15 19.37.41 - A cozy, whimsical scene featuring a steaming hot cup of coffee. The cup should be surrounded by soft pastel colors and a dreamy background. Include de.webp
#         DALL·E 2024-06-15 19.39.03 - A rugged, cozy scene featuring a steaming hot cup of coffee, perfect for a lumberjack in Alaska. The background should include elements like a rustic .webp
#         DALL·E 2024-06-15 19.39.52 - A festive, whimsical scene featuring a steaming hot cup of coffee for Santa Claus. The cup should be surrounded by snowflakes and a winter wonderland .webp
#         DALL·E 2024-06-15 19.42.42 - A whimsical and enchanting scene featuring a steaming hot cup of coffee with a large spoon in it. The background should be filled with soft pastel col.webp
#         DALL·E 2024-06-15 19.43.21 - A whimsical and intriguing scene featuring a steaming hot cup of coffee with a large spoon. The background should incorporate mathematical elements li.webp
#         DALL·E 2024-06-15 19.44.07 - A whimsical and cozy scene featuring a steaming hot cup of coffee with a large spoon inside, set in an environment that hints at a plumber_s life in T.webp
#         DALL·E 2024-06-15 19.44.54 - A whimsical and cozy scene featuring a steaming hot cup of coffee with a large spoon, set against a backdrop inspired by the natural beauty of Kamchat.webp
#         DALL·E 2024-06-15 19.45.43 - A whimsical, tropical scene set in Honolulu featuring a steaming hot cup of coffee. Include elements like a serene beach, palm trees, and clear blue o.webp
#         DALL·E 2024-06-15 19.46.29 - A whimsical and enchanting scene featuring a steaming cup of coffee, set against a backdrop that evokes the charm of Paramaribo. Include elements such.webp
#         DALL·E 2024-06-15 19.47.07 - A contemplative, artistic scene featuring a thinker enjoying a cup of coffee. The setting is inspired by the tropical city of Paramaribo, with lush gr.webp
#         DALL·E 2024-06-15 19.47.49 - A vibrant, tropical scene featuring a steaming hot cup of coffee. The background should include lush, green jungle foliage, exotic flowers, and a hint.webp
#         DALL·E 2024-06-15 19.49.43 - A vibrant and lively scene featuring a steaming cup of coffee, set against a background that captures the essence of Osaka, Japan. Include elements li.webp
#         DALL·E 2024-06-15 19.50.49 - A cozy, whimsical scene set in a charming Czech village, featuring a steaming hot cup of coffee. The background should include picturesque elements li.webp
#         DALL·E 2024-06-15 19.54.55 - A beautiful, vibrant scene of a Buenos Aires street cafe. The cafe should be cozy and inviting, with a steaming hot cup of coffee on a table. The back.webp
#         DALL·E 2024-06-15 19.55.27 - A vibrant scene capturing the essence of Mexico City for a coffee lover. Include iconic elements like the Angel of Independence or colorful street art.webp
#         DALL·E 2024-06-15 19.56.33 - A beautiful scene set in Pénjamo, featuring a steaming hot cup of coffee. The background should include elements that represent Pénjamo, such as tradi.webp
#         Thumbnails (1).png
#     audio/
#         Ambiente/
#             aire acondicionado 1.mp3       
#             ambiente de bosque por la mañana.mp3
#             ambiente de ciudad poco trafico.mp3
#             ambiente de ciudad residencial de noche.mp3
#             ambiente de ciudad, trafico.mp3
#             ambiente de correos.mp3        
#             ambiente de oficina 2.mp3      
#             ambiente peatonal pasos.mp3    
#             andén estación 2 megafonía.mp3 
#             aplausos 10 personas 3 versiones.mp3
#             bostezos [0-3].mp3
#             camión - ambiente de garaje.mp3
#             comer apio lento.mp3
#             elec 01.mp3
#             elec 13.mp3
#             escribir en la pizarra con tiza.mp3
#             estornudo hombre.mp3
#             mujer que estornuda.mp3        
#             mujer que tose.mp3
#             oficina 2.mp3
#             oficina voces ambiente.mp3     
#             palmadas.mp3
#             pasos de hombre  escalera de madera 1.mp3
#             pasos de hombre escalera de madera 4.mp3
#             proyector de diapositiva.mp3   
#             puerta de madera apertura.mp3  
#             puerta de madera chirrido.mp3  
#             puerta golpes con nudillos 10.mp3
#             puerta grande y pessada.mp3    
#             puerta interior chirrido.mp3   
#             risa de grupo de mujeres.mp3   
#         Background/
#             Acelerado_Sonic The Hedgehog OST - Green Hill Zone.mp3
#             Amable_Boat Buds.mp3
#             Chilling_(Audio) Mixkit - Chill Bro (No Copyright Music_Royalty Free Music).m4a
#             Confundido_Animal Crossing City Folk OST_ Nook_s Cranny.mp3
#             Confundido_Shop.mp3
#             Curiosidad-amabilidad_Beach Buds (Short Hike).mp3
#             Esperanzador_Spring (Farm) Extended - HM_ Save the Homeland.mp3
#             Pasar el tiempo - Battle! - wwwWWW.mp3
#             Pasarla bien_Menu - Cooking Mama Soundtrack.mp3
#             Pensativo - Algo Salió Mal_SpongeBob Music Hawaiian.mp3
#             Pensativo Entretenido_Stardew Valley OST - Country Shop.mp3
#             Pillado-hacer una travesura_Able Sisters (Sabel & Mable) - Animal Crossing New Leaf.mp3
#             Relajante Animada_Title Theme - Cooking Mama Soundtrack.mp4
#             Relajante Tranquila_My Time at Portia OST - Spring 2.mp3
#             Trabajando Intensamente_Harold Faltermeyer - Axel F (1984) Beverly Hills Cop - Soundtrack.mp3
#             Trabajando-Investigando_Jean Michel Jarre - Oxygene Part IV original 1976 HQ.mp3
#             Triste _ Hello_.mp3
#             background.mp3
#         Efectos/
#             AWWGHGHAGHAHH (Cough sound effect).mp3
#             Angel - Sound Effect (HD).mp3  
#             CR-Super mario world.mp3       
#             Censor - Sound Effect (HD).mp3 
#             Cricket Sound.mp3
#             Diarrea - efecto de sonido (shitpost).mp3
#             Discord Connect.mp3
#             Discord Desconectarse.mp3      
#             Discord Notificación.mp3       
#             Duck Quack Sound Effect.mp3    
#             Duck Toy Squeak Dog Toy Sound Effect (download).mp3
#             EGreat Grey Wolf Sif Dark Souls.mp3
#             Efecto de Sonido GOLPE.mp3
#             Efecto de sonido escribiendo en teclado pc.mp3
#             Eh.mp3
#             FNAF ambiente 2.mp3
#             Fart with reverb sound effect.mp3
#             Freezing cold (Sound Effect).mp3
#             Funny Turtle Vine, Panting.mp3 
#             Gapa dhapa funny sound effect   no copyright.mp3
#             Gruñido de Monstruo Sonido.mp3 
#             Ha Sound Effect.mp3
#             Halo Clasic Ah.mp3
#             Halo Finish The Fight.mp3      
#             Halo One Final Effort.mp3      
#             Hombre bostezando.mp3
#             Impact sound shitpost.mp3      
#             KAHOOT Music (10 Second Countdown) 3_3.mp3
#             Kahoot Lobby Music.mp3
#             Kanye West - Wolves (Tiene copyright).mp3
#             MSN Sound.mp3
#             Microsoft Windows 95 sonido de inicio.mp3
#             Microsoft Windows XP Error.mp3 
#             Microsoft Windows XP Startup Sound.mp3
#             Microsoft-Windows-XP-Error.mp3 
#             Minecraft Villager (huh) - Sound Effect.mp3
#             Moai sound.mp3
#             Mujer que Ronca - Efecto de Sonido (HD).mp3
#             Mutahar laughing meme Indian guy.mp3
#             OMFG - Hello (audio pobre) [0-5].mp3
#             Old Spice Silbido - Efecto de sonido.mp3
#             Persona hablando con sonidos saturados [0-5].mp3
#             Playstation 2 Startup Noise.mp3
#             Pop sound effect.mp3
#             Poppy Playtime Theme Sad [0-5].mp3
#             Practice mode geometry dash.mp3
#             Psst sound effect (DOORS).mp3  
#             ROBLOX Oof Sound Effect.mp3    
#             Risa de ibai.mp3
#             Roblox - sonido perturbador.mp3
#             Roncar Ronquidos Efecto.mp3    
#             SKYPE CALL SOUND.mp3
#             Sneeze Sound Effect #2.mp3     
#             Sniffing Sound Effect.mp3      
#             Sonido bostezo.mp3
#             Sonido de perturbación-incomodidad.mp3
#             Spongebob Boo-womp Sound Effect.mp3
#             Suspense climax Sound effect.mp3
#             THX Theme [12-18].mp3
#             Taca a Xereca pra Min [0-5].mp3
#             Tsk Tsk (Solo el final).mp3    
#             WOMAN COUGHING SOUND EFFECTS.mp3
#             Windows 11 Startup Sound.mp3   
#             Wow sound effect.mp3
#             [GREEN SCREEN] Windows XP Error.mp4
#             cartoon running sound effect.mp3
#             climax sound effect.mp3        
#             cof_corto_hombre.mp3
#             cof_largo_hombre.mp3
#             cof_woman.mp3
#             eructos.mp3
#             música perturbadora.mp3        
#             shhhhhhhhh sound.mp3
#             sonido de impacto.mp3
#             sonido golpe en la cabeza.mp3  
#             suspense sound effect. No copyright.mp3
#         Endings/
#             END1.mp4
#             END1_V.mp4
#             END2.mp4
#             END2_V.mp4
#     fondos/
#         Cafetería/
#             Fondos de personajes (1).png   
#             Fondos de personajes (2).png   
#             Fondos de personajes (3).png   
#             Fondos de personajes (4).png   
#             Fondos de personajes (5).png   
#             Fondos de personajes.png       
#         Calle/
#             Fondos de personajes (1).png   
#             Fondos de personajes (2).png   
#             Fondos de personajes (3).png   
#             Fondos de personajes (4).png   
#             Fondos de personajes (5).png   
#             Fondos de personajes.png       
#         Elevador/
#             Fondos de personajes (1).png   
#             Fondos de personajes (2).png
#             Fondos de personajes (3).png   
#             Fondos de personajes (4).png   
#             Fondos de personajes (5).png   
#             Fondos de personajes.png       
#         Oficina/
#             Fondos de personajes (1).png   
#             Fondos de personajes (2).png   
#             Fondos de personajes (3).png   
#             Fondos de personajes (4).png   
#             Fondos de personajes (5).png   
#             Fondos de personajes.png       
#         Parque/
#             Fondos de personajes (1).png   
#             Fondos de personajes (2).png   
#             Fondos de personajes (3).png   
#             Fondos de personajes (4).png   
#             Fondos de personajes (5).png   
#             Fondos de personajes.png       
#         Pasillo/
#             Fondos de personajes (1).png   
#             Fondos de personajes (2).png   
#             Fondos de personajes (3).png   
#             Fondos de personajes (4).png   
#             Fondos de personajes (5).png   
#             Fondos de personajes.png       
#         Puerta/
#             Fondos de personajes (1).png   
#             Fondos de personajes (2).png   
#             Fondos de personajes (3).png   
#             Fondos de personajes (4).png   
#             Fondos de personajes (5).png   
#             Fondos de personajes.png       
#         Sala/
#             Fondos de personajes (1).png   
#             Fondos de personajes (2).png   
#             Fondos de personajes (3).png   
#             Fondos de personajes (4).png   
#             Fondos de personajes (5).png   
#             Fondos de personajes.png       
#         Tren/
#             Fondos de personajes (1).png   
#             Fondos de personajes (2).png   
#             Fondos de personajes (3).png   
#             Fondos de personajes (4).png   
#             Fondos de personajes (5).png   
#             Fondos de personajes.png       
#     personajes/
#         Descripciones/
#             Avances_Personajes_Memorias_de_7.csv.csv
#         personajes_animales/
#             Cactus/
#                 A_left.png
#                 angry_left.png
#                 angry_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_left.png
#                 happy_right.png
#                 realistic_chair.png        
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png        
#             Coneja/
#                 angry_left.png
#                 angry_right.png
#                 confused_left.png
#                 confused_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_front.png
#                 happy_left.png
#                 happy_right.png
#                 realistic_chair.png        
#                 realistic_photo.png        
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png        
#             Conejo/
#                 A_left.png
#                 A_right.png
#                 angry_left.png
#                 angry_right.png
#                 confused_left.png
#                 confused_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_left.png
#                 happy_right.png
#                 realistic_chair.png        
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png        
#             Gata/
#                 A_right.png
#                 Correct_A_left.png
#                 Correct_happy_left.png     
#                 Correct_surprised_left.png 
#                 angy_left.png
#                 confused_left.png
#                 happy_right.png
#                 realistic_chair.png        
#                 serious_left.png
#                 surprised_right.png        
#             Kiwi/
#                 A_right.png
#                 Correct_A_left.png
#                 Correct_happy_left.png     
#                 Correct_surprised_left.png 
#                 angry_left.png
#                 angry_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_front.png
#                 happy_right.png
#                 realistic_chair.png        
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png        
#             Pata/
#                 A_left.png
#                 angry_left.png
#                 angry_right.png
#                 confused_front.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_left.png
#                 realistic_chair.png        
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_front.png        
#                 worried_left.png
#             Pato/
#                 A_left.png
#                 A_right.png
#                 Correct_happy_left.png     
#                 angry_left.png
#                 angry_right.png
#                 condused_right.png
#                 confused_left.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_right.png
#                 realistic_chair.png        
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#             Pollo/
#                 A_right.png
#                 Correct_A_left.png
#                 angry_left.png
#                 angry_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_left (2).png
#                 happy_left.png
#                 happy_right (2).png        
#                 happy_right.png
#                 realistic_chair.png        
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png        
#             Rinoceronte Rojo/
#                 A_right.png
#                 Correct_A_left.png
#                 Correct_happy_left.png     
#                 angry_left.png
#                 angry_right.png
#                 confused_left.png
#                 confused_right.png
#                 happy_right.png
#                 realistic_A.png
#                 realistic_chair.png        
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png        
#             Roca/
#                 A_left.png
#                 A_right.png
#                 angy_left.png
#                 angy_right.png
#                 dizzy_left.png
#                 dizzy_right.png
#                 happy_left.png
#                 happy_right.png
#                 realistic_chair.png        
#                 sad_left.png
#                 sad_right.png
#                 serious_left.png
#                 serious_right.png
#                 surprised_left.png
#                 surprised_right.png        
#             Tortuga/
#                 tortuga1.png
#                 tortuga1png.png
#                 tortuga_office.png
# modules/
#     __init__.py
#     __pycache__/
#         __init__.cpython-312.pyc
#         character_manager.cpython-312.pyc
#         file_utils.cpython-312.pyc
#         image_processing.cpython-312.pyc
#         positions.cpython-312.pyc
#         script_parser.cpython-312.pyc
#         utils.cpython-312.pyc
#     audio_utils.py
#     character_manager.py
#     file_utils.py
#     image_processing.py
#     openai_mod.py
#     positions.py
#     script_parser.py
#     utils.py
#     video_effects.py
# requirements.txt