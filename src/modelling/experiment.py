from scipy.stats import expon
from hyperopt import fmin, tpe

from ..utils.functions import split_features_target, enrich_df_with_predictions, rmse


class HyperParamExperiment:
    def __init__(self, model, train, loss="reg:squarederror", random_state=1):
        self.model = model
        self.loss = loss
        self.random_state = random_state
        self.train = train
        self.X_train, self.y_train = split_features_target(self.train)
        self.logs = []

    def get_trained_model(self, kwargs={"sample_weight_lam": 1e-8}):
        sample_weight = self.get_sample_weight(kwargs.pop("sample_weight_lam"))
        m = self.model(seed=self.random_state, objective=self.loss, **kwargs)
        m.fit(self.X_train, self.y_train, sample_weight=sample_weight)
        return m

    def objective_function(self, kwargs):
        log = {"params": kwargs.copy()}
        m = self.get_trained_model(kwargs.copy())
        pred = m.predict(self.X_score)
        df = enrich_df_with_predictions(self.score, pred)

        target = rmse(self.y_score, pred)
        log["target"] = target
        self.logs.append(log)
        return target

    def get_sample_weight(self, lam):
        return expon.pdf((self.train.F_DATE.max() - self.train.F_DATE).dt.days / 365, scale=1 / lam)

    def run(self, score, space, algo=tpe.suggest, n_iter=10):
        self.score = score
        self.X_score, self.y_score = split_features_target(self.score)
        self.space = space
        self.algo = algo
        self.n_iter = n_iter
        self.best_trial = fmin(fn=self.objective_function,
                               space=self.space,
                               algo=self.algo,
                               max_evals=self.n_iter)

        return self.get_trained_model(self.best_trial)
