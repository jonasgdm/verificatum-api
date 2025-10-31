from screens import home, benchmark
from app import router

from screens.sim import (
    descrp,
    keygen,
    mix,
    mock,
    result,
    setup,
    sim_menu,
)
from screens.mix import (
    shuffle_setup,
    single_shuffle,
    shuffle_result,
    show_final_tally,
    show_ciphertexts,
)


def main():
    # registra as telas aqui

    router.ROUTES["home"] = home.show
    router.ROUTES["sim.descrp"] = descrp.show
    router.ROUTES["sim.sim_menu"] = sim_menu.show
    router.ROUTES["sim.setup"] = setup.show
    router.ROUTES["sim.keygen"] = keygen.show
    router.ROUTES["sim.mock"] = mock.show
    router.ROUTES["sim.result"] = result.show

    router.ROUTES["mix.shuffle_setup"] = shuffle_setup.show
    router.ROUTES["mix.single_shuffle"] = single_shuffle.show
    router.ROUTES["mix.shuffle_result"] = shuffle_result.show
    router.ROUTES["mix.show_final_tally"] = show_final_tally.show
    # router.ROUTES["mix.show_ciphertexts"] = show_ciphertexts.show

    router.ROUTES["benchmark"] = benchmark.show

    router.run("home")


if __name__ == "__main__":
    main()
