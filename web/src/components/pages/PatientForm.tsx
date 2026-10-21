"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useI18n } from "@/lib/i18n/context";
import type { Gender } from "@/lib/session/reducer";
import { useSession } from "@/lib/session/context";

const GENDERS: { value: Gender; key: "patient.gender.female" | "patient.gender.male" | "patient.gender.other" | "patient.gender.unsaid" }[] = [
  { value: "female", key: "patient.gender.female" },
  { value: "male", key: "patient.gender.male" },
  { value: "other", key: "patient.gender.other" },
  { value: "prefer_not_to_say", key: "patient.gender.unsaid" },
];

export function ageError(value: string): boolean {
  if (!/^\d{1,3}$/.test(value.trim())) return true;
  const age = Number(value);
  return age < 0 || age > 120;
}

export function PatientForm() {
  const { t } = useI18n();
  const { state, dispatch } = useSession();
  const router = useRouter();
  const [asking, setAsking] = useState(state.patient.confirmed);
  const [showAgeError, setShowAgeError] = useState(false);
  const [showGenderError, setShowGenderError] = useState(false);
  const h1 = t("patient.h1");
  const lede = t("patient.lede");
  const age = t("patient.age");
  const gender = t("patient.gender");
  const cont = t("action.continue");
  const yes = t("action.yesContinue");
  const edit = t("action.edit");
  const ageMessage = t("patient.ageError");
  const genderMessage = t("patient.genderError");
  const ask = t("patient.askBefore");
  const year = t("patient.yearOld");
  const chosen = GENDERS.find((item) => item.value === state.patient.gender);
  const chosenLabel = chosen ? t(chosen.key) : null;

  if (asking && chosenLabel && !ageError(state.patient.ageYears)) {
    return (
      <div className="stack">
        <h1 lang={h1.locale}>{h1.text}</h1>
        <p>
          <span lang={ask.locale}>{ask.text}</span> {state.patient.ageYears.trim()}-
          <span lang={year.locale}>{year.text}</span> <span lang={chosenLabel.locale}>{chosenLabel.text}</span>?
        </p>
        <div className="actions">
          <button
            type="button"
            className="btn btn-primary"
            lang={yes.locale}
            onClick={() => {
              dispatch({ type: "confirmPatient" });
              router.push("/results");
            }}
          >
            {yes.text}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            lang={edit.locale}
            onClick={() => {
              dispatch({ type: "editPatient" });
              setAsking(false);
            }}
          >
            {edit.text}
          </button>
        </div>
      </div>
    );
  }

  return (
    <form
      className="stack"
      onSubmit={(event) => {
        event.preventDefault();
        const badAge = ageError(state.patient.ageYears);
        const badGender = state.patient.gender === "";
        setShowAgeError(badAge);
        setShowGenderError(badGender);
        if (!badAge && !badGender) setAsking(true);
      }}
    >
      <h1 lang={h1.locale}>{h1.text}</h1>
      <p className="lede" lang={lede.locale}>
        {lede.text}
      </p>
      <label className="field" htmlFor="age-years" lang={age.locale}>
        {age.text}
        <input
          id="age-years"
          inputMode="numeric"
          autoComplete="off"
          value={state.patient.ageYears}
          aria-invalid={showAgeError}
          aria-describedby={showAgeError ? "age-error" : undefined}
          onChange={(event) => dispatch({ type: "setAge", ageYears: event.target.value })}
        />
      </label>
      {showAgeError ? (
        <p id="age-error" role="alert" lang={ageMessage.locale}>
          {ageMessage.text}
        </p>
      ) : null}
      <fieldset>
        <legend lang={gender.locale}>{gender.text}</legend>
        {GENDERS.map((item) => {
          const label = t(item.key);
          return (
            <label key={item.value} className="check">
              <input
                type="radio"
                name="gender"
                value={item.value}
                checked={state.patient.gender === item.value}
                onChange={() => dispatch({ type: "setGender", gender: item.value })}
              />
              <span lang={label.locale}>{label.text}</span>
            </label>
          );
        })}
      </fieldset>
      {showGenderError ? (
        <p id="gender-error" role="alert" lang={genderMessage.locale}>
          {genderMessage.text}
        </p>
      ) : null}
      <div className="actions">
        <button type="submit" className="btn btn-primary" lang={cont.locale}>
          {cont.text}
        </button>
      </div>
    </form>
  );
}
