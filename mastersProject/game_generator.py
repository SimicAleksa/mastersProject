from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


def generate_game_from_prompt(prompt):
    textXfile = open('gameDSL.tx', 'r')
    grammar = textXfile.read()
    textXfile.close()

    exampleGameFile = open('testGame.game', 'r')
    exampleGame = exampleGameFile.read()
    exampleGameFile.close()

    interpreterFile = open('interpreter.py', 'r')
    interpreter = interpreterFile.read()
    interpreterFile.close()

    client = OpenAI(
        api_key=os.environ.get("OPENAI_KEY"),
    )

    response = client.chat.completions.create(
        model=os.environ.get("GPT_MODEL"),
        messages=[
            {"role": "system", "content": f"Create a game using the following "
                                          f"TextX grammar file -> {grammar} and here is the example of how the "
                                          f"generated game could look like-> {exampleGame}. Just give me the game code "
                                          f"itself and nothing more. Here is the interpreter for the game you are "
                                          f"about to generate -> {interpreter}. Be careful not to mix up"
                                          f" weapons and items. Weapons are entity for themselves! Also add a region"
                                          f"that will be used to end the game, so that when the player steps into it"
                                          f"the game ends. I mean the final region should be region after the final region"},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the generated game description
    game_description = response.choices[0].message.content

    # Save this to a file
    with open("generatedGame.game", "w") as file:
        file.write(game_description)

    return "generatedGame.game"
