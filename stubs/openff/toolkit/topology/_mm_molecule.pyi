from collections.abc import Generator
from typing import Dict, List, NoReturn, Union

import networkx as nx
from _typeshed import Incomplete
from openff.toolkit.topology.molecule import Molecule as Molecule
from openff.units.unit import Quantity as Quantity

class _SimpleMolecule:
    atoms: Incomplete
    bonds: Incomplete
    hierarchy_schemes: Incomplete
    conformers: Incomplete
    def __init__(self) -> None: ...
    def add_atom(self, atomic_number: int, **kwargs): ...
    def add_bond(self, atom1, atom2, **kwargs) -> None: ...
    def add_conformer(self, conformer) -> None: ...
    @property
    def n_atoms(self) -> int: ...
    @property
    def n_bonds(self) -> int: ...
    @property
    def n_conformers(self) -> int: ...
    def atom(self, index): ...
    def atom_index(self, atom) -> int: ...
    def bond(self, index): ...
    def get_bond_between(self, atom1_index, atom2_index): ...
    @property
    def angles(self) -> Generator[Incomplete, None, None]: ...
    @property
    def propers(self) -> Generator[Incomplete, None, None]: ...
    @property
    def impropers(self): ...
    @property
    def smirnoff_impropers(self): ...
    @property
    def amber_impropers(self): ...
    @property
    def hill_formula(self) -> str: ...
    def to_hill_formula(self) -> str: ...
    def to_networkx(self) -> nx.Graph: ...
    def nth_degree_neighbors(self, n_degrees): ...
    def to_dict(self) -> Dict: ...
    @classmethod
    def from_dict(cls, molecule_dict): ...
    @classmethod
    def from_molecule(cls, molecule: Molecule): ...
    def to_molecule(self) -> NoReturn: ...
    def generate_unique_atom_names(self) -> None: ...

class _SimpleAtom:
    metadata: Incomplete
    def __init__(
        self,
        atomic_number: int,
        molecule: Incomplete | None = ...,
        metadata: Incomplete | None = ...,
        **kwargs
    ) -> None: ...
    @property
    def atomic_number(self) -> int: ...
    @atomic_number.setter
    def atomic_number(self, value) -> None: ...
    @property
    def symbol(self) -> str: ...
    @property
    def mass(self) -> Quantity: ...
    @property
    def molecule(self): ...
    @property
    def bonds(self): ...
    def add_bond(self, bond) -> None: ...
    @property
    def bonded_atoms(self) -> Generator[Incomplete, None, None]: ...
    @property
    def molecule_atom_index(self) -> int: ...
    def to_dict(self) -> Dict[str, Union[Dict, str, int]]: ...
    @classmethod
    def from_dict(cls, atom_dict: Dict): ...

class _SimpleBond:
    molecule: Incomplete
    atom1: Incomplete
    atom2: Incomplete
    def __init__(self, atom1, atom2, **kwargs) -> None: ...
    @property
    def atoms(self) -> List[_SimpleAtom]: ...
    @property
    def atom1_index(self) -> int: ...
    @property
    def atom2_index(self) -> int: ...
    def to_dict(self) -> Dict: ...
