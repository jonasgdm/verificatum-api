from screens import home
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
from screens.mix import shuffle_setup


def main():
    # registra as telas aqui

    router.ROUTES["home"] = home.show
    router.ROUTES["sim.descrp"] = descrp.show
    router.ROUTES["sim.sim_menu"] = sim_menu.show
    router.ROUTES["sim.setup"] = setup.show
    router.ROUTES["sim.keygen"] = keygen.show
    router.ROUTES["sim.mock"] = mock.show
    router.ROUTES["sim.result"] = result.show

    router.ROUTES["mix.setup"] = shuffle_setup.show

    router.run("sim.result")


if __name__ == "__main__":
    main()
