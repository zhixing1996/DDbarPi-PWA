import os, collections, yaml

scan = collections.namedtuple('scan', 'path mass width NLL')

class scan_seq:
    def __init__(self, resonance, path, decimal):
        self._resonance = resonance
        self._scan_path = path
        self._decimal = decimal
        scans = []
        for p in os.listdir(path):
            with open(p + '/final_params.json') as f:
                result = yaml.load(f, yaml.FullLoader)
            path = p
            mass = result['value'][resonance + '_mass']
            width = result['value'][resonance + '_width']
            NLL = result['status']['NLL']
            scans.append(scan(path, mass, width, NLL))
        self._scans = scans

    def mass_width_nll(self):
        import numpy as np
        import matplotlib.pyplot as plt
        mass, width, nll = [], [], {}
        for scan in self._scans:
            mass.append(scan.mass)
            width.append(scan.width)
            index = str(scan.mass) + '_' + str(scan.width)
            nll[index] = scan.nll
        massn = np.unique(mass)
        widthn = np.unique(width)
        MASSm, WIDTHm = np.meshgrid(massn, widthn)
        nllm = []
        temp = []
        for m in massn:
            for w in widthn:
                idx = str(m) + '_' + str(w)
                NLL = nll[idx]
                temp.append(NLL)
            nllm.append(temp)
            temp = []
        NLLm = np.array(nllm)
        plot = plt.pcolormesh(MASSm, WIDTHm, NLLm, cmap='RdBu', shading='gouraud')
        cset = plt.contour(MASSm, WIDTHm, NLLm, cmap = 'gray')
        plt.xlabel('mass (GeV)', fontsize = 10)
        plt.ylabel('width (GeV)', fontsize = 10)
        plt.xticks(fontsize = 10)
        plt.yticks(fontsize = 10)
        plt.tight_layout()
        plt.clabel(cset, inline = True)
        plt.colorbar(plot)
        if not os.path.exists('./figs/'): os.makedirs('./figs/')
        plt.savefig('./figs/' + str(self._resonance) + '_mass_width_scan.pdf', dpi = 400, bbox_inches = 'tight')
        plt.show()

    def __len__(self):
        return len(self._scans)

    def __getitem__(self, position):
        return self._scans[position]

    def __repr__(self):
        return '<mass and width scan of {} with {} GeV decimal>'.format(self._resonance, self._decimal)
