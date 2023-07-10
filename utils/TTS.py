import os
import torch


def silero_tts(tts, language="en", model="v3_en", speaker="en_50"):
    device = torch.device("cpu")
    torch.set_num_threads(4)
    local_file = "model.pt"

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(
            f"https://models.silero.ai/models/tts/{language}/{model}.pt", local_file
        )

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    example_text = "i'm fine thank you and you?"
    sample_rate = 48000

    audio_paths = model.save_wav(text=tts, speaker=speaker, sample_rate=sample_rate)


def silero_tts_ru(tts, language="ru", model="v3_1_ru", speaker="xenia"):
    device = torch.device("cpu")
    torch.set_num_threads(4)
    local_file = "model1.pt"

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(
            f"https://models.silero.ai/models/tts/{language}/{model}.pt", local_file
        )

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    example_text = "Я в порядке, спасибо, а ты?"
    sample_rate = 48000

    audio_paths = model.save_wav(text=tts, speaker=speaker, sample_rate=sample_rate)


def silero_tts_fr(tts, language="fr", model="v3_fr", speaker="fr_4"):
    device = torch.device("cpu")
    torch.set_num_threads(4)
    local_file = "model2.pt"

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(
            f"https://models.silero.ai/models/tts/{language}/{model}.pt", local_file
        )

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    example_text = "Je vais bien, merci, et vous ?"
    sample_rate = 48000

    audio_paths = model.save_wav(text=tts, speaker=speaker, sample_rate=sample_rate)


def silero_tts_es(tts, language="es", model="v3_es", speaker="es_0"):
    device = torch.device("cpu")
    torch.set_num_threads(4)
    local_file = "model3.pt"

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(
            f"https://models.silero.ai/models/tts/{language}/{model}.pt", local_file
        )

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    example_text = "Estoy bien, gracias, ¿y tú?"
    sample_rate = 48000

    audio_paths = model.save_wav(text=tts, speaker=speaker, sample_rate=sample_rate)


def silero_tts_de(tts, language="de", model="v3_de", speaker="eva_k"):
    device = torch.device("cpu")
    torch.set_num_threads(4)
    local_file = "model4.pt"

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(
            f"https://models.silero.ai/models/tts/{language}/{model}.pt", local_file
        )

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    example_text = "Mir geht es gut, danke, und Ihnen?"
    sample_rate = 48000

    audio_paths = model.save_wav(text=tts, speaker=speaker, sample_rate=sample_rate)


if __name__ == "__main__":
    silero_tts()
